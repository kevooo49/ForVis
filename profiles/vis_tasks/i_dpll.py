import operator
import time
import os
import marshal

# CONSTANT
VERSION = 'FINAL_v0.1'
SAT = 1
UNSAT = 0
UNRESOLVED = -1
K_MOMS = 1024  # 2^10, k = 10


class DpllIteration:
    def __init__(self, cnf_file=None, heuristic_type=3):
        self.cnf_file = cnf_file
        self.heuristic_type = heuristic_type
        self.assignment_list, self.assignment_trail = [], []
        self.formula_backtrack_l, self.assign_backtrack_l, self.decision_backtrack_l = {}, {}, {}
        self.conflict_cnt, self.split_cnt, self.decision_cnt, self.var_cnt, self.clause_cnt = 0, 0, 0, 0, 0
        self.f_list, self.v_list = {}, {}
        # f_list: {key:value} = {clause number: [clause]}
        # v_list: {key:value} = {lit: [list of clause numbers in which lit occurs]}

    @staticmethod
    def check_formula(formula, assignment):
        i = 1
        for clause in formula.values():
            lit_value = []
            for lit in clause:
                if lit in assignment:
                    lit_value.append(1)
                else:
                    if -lit in assignment:
                        lit_value.append(0)
                    else:
                        lit_value.append(-1)
            clause_value = max(lit_value)
            print("%3s" % i, ".", "%20s" % clause, "%20s" % lit_value, "%20s" % clause_value)
            i += 1

    # open cnf file and read all clauses
    def open_cnf_file(self, file_name):
        s = ''
        clause_nr = 0
        f = open(file_name, "r")
        for line in f:
            if line.startswith('c'):
                continue
            if line.startswith('p cnf'):
                continue
            if line[0] != 'c':
                if line[0] != 'p':  # zakladam, ze clause konczy ' 0'
                    ind = line.find(' 0')  # zwraca -1 jesli nie ma '0' w linii
                    if ind == -1:  # jesli nie ma '0' w linii to zapamietuje linie bez ostatniego znaku '\n'
                        s = line[0:-1] + ' '
                    if ind > 0:  # jesli jest '0' to wpisuje linie do formuly jako clause
                        s = s + line
                        try:
                            clause = [int(lit) for lit in s[:-2].split()]
                        except ValueError:
                            print('This is not proper file format in line', clause_nr, '. Line discarded.')
                            continue
                        self.f_list[clause_nr] = clause
                        self.add_variable(clause, clause_nr)
                        s = ''
                        clause_nr += 1

    def add_variable(self, clause, clause_nr):
        for lit in clause:
            try:
                self.v_list[lit].append(clause_nr)
            except KeyError:
                self.v_list[lit] = [clause_nr]

    # tworzenie listy literal z listy formula
    @staticmethod
    def literal(f_list):
        literal_list = []
        for clause in f_list.values():
            for lit in clause:
                if lit not in literal_list:
                    literal_list.append(lit)
        return literal_list

    # tworzenie listy variable z listy literal
    @staticmethod
    def variable(f_list):
        variable_list = []
        for clause in f_list.values():
            for lit in clause:
                v = abs(lit)
                if v not in variable_list:
                    variable_list.append(v)
        return variable_list

    # Unit clause: clause containing only single literal, i.e. (1), i.e. (-2)
    #   * remove all clauses containing single literal
    #   * remove all instances of negation literal from every clause in formula F
    # i.e. unit_list: [-52, 53]
    @staticmethod
    def unit_clause(f_list):
        unit_l = []

        for clause in f_list.values():
            if len(clause) == 1:
                lit = clause[0]
                if (lit not in unit_l) and (-lit not in unit_l):
                    unit_l.append(lit)
        return unit_l

    # unit propagation
    def unit_propagation(self, unit_list):
        new_unit_list, conflict = [], False

        for lit in unit_list:
            # delete clauses contained lit
            if lit in self.v_list:
                for clause_nr in self.v_list[lit]:
                    if clause_nr in self.f_list:
                        del self.f_list[clause_nr]

            # delete -lit from clauses
            if -lit in self.v_list:
                for clause_nr in self.v_list[-lit]:
                    if clause_nr in self.f_list:
                        self.f_list[clause_nr].remove(-lit)
                        cl = self.f_list[clause_nr]
                        if not cl:  # check if conflict
                            conflict = True
                            break
                        if len(cl) == 1:  # check if unit clause
                            literal = self.f_list[clause_nr][0]
                            if literal not in new_unit_list and literal not in unit_list:
                                new_unit_list.append(literal)

            self.assignment_list.append(lit)

            if conflict:
                self.assignment_trail.append(lit)
                self.assignment_trail.append('c')
                break
            else:
                self.assignment_trail.append(lit)

        return conflict, new_unit_list

    def heuristic(self, heuristic_nr, f_list):

        # Dynamic Largest Individual Sum heuristic
        def dlis(f_list):
            lit_cnt = {}
            for clause in f_list.values():
                for lit in clause:
                    try:
                        lit_cnt[lit] += 1
                    except KeyError:
                        lit_cnt[lit] = 1
            lit = max(lit_cnt.items(), key=operator.itemgetter(1))[0]
            return lit

        # Jeroslow Wang heuristic
        def jeroslow_wang(f_list):
            jw = {}

            for clause in f_list.values():
                for lit in clause:
                    try:
                        jw[lit] += 2 ** (-len(clause))
                    except KeyError:
                        jw[lit] = 2 ** (-len(clause))

            lit = max(jw.items(), key=operator.itemgetter(1))[0]
            return lit

        # Maximum Occurence of clauses of Minimum Size
        def moms(f_list):
            pos, neg, moms_max = {}, {}, 0

            formula_list = list(f_list.values())
            # looking for min length clauses
            formula_list.sort(key=len)
            min_clause_length = len(formula_list[0])

            for clause in formula_list:
                l_cl = len(clause)
                if l_cl == min_clause_length:
                    for lit in clause:
                        if lit > 0:
                            try:
                                pos[lit] += 1
                            except KeyError:
                                pos[lit] = 1
                            if -lit not in neg:  # set neg = 0 for -lit
                                neg[-lit] = 0
                        else:  # lit < 0
                            try:
                                neg[lit] += 1
                            except KeyError:
                                neg[lit] = 1
                            if -lit not in pos:  # set pos = 0 for -lit
                                pos[-lit] = 0
                elif l_cl > min_clause_length:
                    break

            for lit, pos_value in pos.items():
                neg_value = neg[-lit]
                moms_value = (pos_value + neg_value) * K_MOMS + pos_value * neg_value
                if moms_value > moms_max:
                    moms_max = moms_value
                    moms_lit = lit

            return moms_lit

        # Two-sided Jeroslow Wang heuristic
        def jeroslow_wang_two(f_list):
            jw_pos, jw_neg = {}, {}

            for clause in f_list.values():
                for lit in clause:
                    if lit > 0:
                        try:
                            jw_pos[lit] += 2 ** (-len(clause))
                        except KeyError:
                            jw_pos[lit] = 2 ** (-len(clause))
                        if -lit not in jw_neg:
                            jw_neg[-lit] = 0
                    else:
                        try:
                            jw_neg[lit] += 2 ** (-len(clause))
                        except KeyError:
                            jw_neg[lit] = 2 ** (-len(clause))
                        if -lit not in jw_pos:
                            jw_pos[-lit] = 0
            jw_max = 0
            for lit in jw_pos.keys():
                jw_p = jw_pos[lit]
                jw_n = jw_neg[-lit]
                jw = jw_p + jw_n
                if jw >= jw_max:
                    jw_max = jw
                    if jw_p >= jw_n:
                        jw_lit = lit
                    else:
                        jw_lit = -lit
            return jw_lit

        # Dynamic Largest Individual Sum heuristic
        def weighted_dlis(f_list):
            l2_cnt = {}
            l3_cnt = {}
            literal_l = self.literal(f_list)
            wdlis_max = 0
            wdlis_lit = literal_l[0]

            for clause in f_list.values():
                l_cl = len(clause)
                for lit in clause:
                    if l_cl == 2:
                        try:
                            l2_cnt[lit] += 1
                        except KeyError:
                            l2_cnt[lit] = 1
                    if l_cl == 3:
                        try:
                            l3_cnt[lit] += 1
                        except KeyError:
                            l3_cnt[lit] = 1
            for lit in literal_l:
                try:
                    l2_val = l2_cnt[lit]
                except KeyError:
                    l2_val = 0
                try:
                    l3_val = l3_cnt[lit]
                except KeyError:
                    l3_val = 0
                wdlis_value = 5 * l2_val + l3_val
                if wdlis_value >= wdlis_max:
                    wdlis_max = wdlis_value
                    wdlis_lit = lit
            return wdlis_lit

        dispatch = {1: dlis, 2: jeroslow_wang, 3: moms, 4: jeroslow_wang_two, 5: weighted_dlis}
        lit = dispatch[heuristic_nr](f_list)
        return lit

    def conflict_analyze(self):
        dec_lev_to_delete, back_lit, back_dec_level = [], 0, -1
        self.conflict_cnt += 1  # conflicts counter

        dict_keys = list(self.decision_backtrack_l.keys())
        dict_keys.reverse()
        for dec_level in dict_keys:
            dec_var = self.decision_backtrack_l[dec_level]
            l_dec_var = len(dec_var)  # value of decision_backtrack_l = [lit, -lit] if -lit was assigned
            if l_dec_var == 1:
                back_dec_level = dec_level
                back_lit = -dec_var[0]
                self.assignment_trail.append('b')
                self.assignment_trail.append(-back_lit)
                break
            else:
                dec_lev_to_delete.append(dec_level)

        # delete decision levels from backtracks
        if dec_lev_to_delete:
            for d in dec_lev_to_delete:
                del self.decision_backtrack_l[d]
                del self.assign_backtrack_l[d]
                del self.formula_backtrack_l[d]

        return back_dec_level, back_lit

    def dpll(self):
        result, conflict, decision_level, lit = UNRESOLVED, False, 0, 0
        # just for tests
        self.var_cnt = len(self.variable(self.f_list))
        self.clause_cnt = len(self.f_list)

        # check if formula SAT
        if not self.f_list:
            self.assignment_trail.append('sat')
            return SAT

        # check if formula UNSAT
        for clause in self.f_list.values():
            if not clause:
                self.assignment_trail.append('unsat')
                return UNSAT

        # unit propagation before branching any literals by decision
        unit_list = self.unit_clause(self.f_list)
        while unit_list:
            conflict, unit_list = self.unit_propagation(unit_list)
            if conflict:
                self.assignment_trail.append('unsat')
                return UNSAT

        # idpll loop
        while result == UNRESOLVED:
            conflict = False

            while unit_list:
                conflict, unit_list = self.unit_propagation(unit_list)
                if conflict:
                    decision_level, lit = self.conflict_analyze()  # dec level and lit get back from backtracks
                    if decision_level < 0:  # there was True and False assignment to the root variable
                        self.assignment_trail.append('unsat')
                        return UNSAT
                    break

            if not conflict:  # no conflict # check if formula empty -> SAT
                if not self.f_list:
                    self.assignment_trail.append('sat')
                    return SAT

                decision_level += 1  # increase decision level
                self.decision_cnt += 1  # counters just for statistic reports
                self.formula_backtrack_l[decision_level] = marshal.loads(marshal.dumps(self.f_list))
                self.assign_backtrack_l[decision_level] = marshal.loads(marshal.dumps(self.assignment_list))
                lit = self.heuristic(self.heuristic_type, self.f_list)  # lit selection using heuristic: 1:'dlis', 2:'jw', 3:'moms'
                unit_list = [lit]  # add lit to unit_list
                self.decision_backtrack_l[decision_level] = [lit]  # decision_lit    # add decision_lit to bactrack
                self.assignment_trail.append('d')  # for solution tree visualization
                self.assignment_trail.append(lit)
                result = UNRESOLVED  # set result
            else:  # split: dec_level and lit get back from backtracks
                self.split_cnt += 1  # counters just for statistic reports
                # return formula and assignment from backtrack
                self.f_list = self.formula_backtrack_l[decision_level]
                self.assignment_list = self.assign_backtrack_l[decision_level]
                unit_list = [lit]  # add lit to unit_list
                self.decision_backtrack_l[decision_level].append(lit)  # add lit to decision_lit -> to bactrack
                self.assignment_trail.append('d')  # for tree visualization
                self.assignment_trail.append(lit)
                result = UNRESOLVED

    def test_run(self):
        cnf_path = 'C:\\Users\\Norbi\\Desktop\\inz\\cnf_files\\CNF\\heu_test\\'
        cnf_folders = sorted(os.listdir(cnf_path))
        print(cnf_folders)

        log = 'i_dpll_log.out'
        stat = 'i_dpll_static.out'
        glob = 'i_dpll_global.out'
        assign = 'assignment_trail.out'

        fs = open(stat, 'a')
        fs.writelines(str("No;    FILE;            RESULT;   DECISION;   CNFL;   TIME \n"))
        fs.writelines(str("-----------------------------------------------------------\n"))
        fs.close()

        fg = open(glob, 'a')
        fg.writelines(
            'Set    Clause  Vars  Clauses  SAT/UNSAT   Global   Min    Max     Avg     Min    Max    Avg    Min   Max    Avg\n')
        fg.writelines(
            'Test   Length                             time    time    time    time       decisions           conflicts\n')
        fg.close()

        for cnf_folder in cnf_folders:
            sat_cnt, unsat_cnt = 0, 0
            dec_cnt, avg_dec, cnfl_cnt, avg_cnfl = 0, 0, 0, 0
            avg_time = 0
            global_runtime = 0
            cnf_files = sorted(
                file for file in os.listdir(cnf_path + cnf_folder) if file.endswith('.cnf') or file.endswith('.txt'))
            test_set = cnf_folder

            i = 1
            for file in cnf_files:
                print(i, '. ', cnf_path + cnf_folder + '/' + file)
                self.open_cnf_file(cnf_path + cnf_folder + '/' + file)

                # for test files RANDOM 3-SAT sat or unsat cnf file
                f_name = cnf_files[0]
                if f_name[0:2] == 'uf':
                    test_set = f_name[0:5]
                elif f_name[0:2] == 'uu':
                    test_set = f_name[0:6]

                start_time = time.time()
                result = self.dpll()
                runtime = (time.time() - start_time)
                global_runtime += runtime

                fa = open(assign, 'w')
                fa.writelines(self.assignment_trail)
                fa.close()

                if i == 1:
                    min_time, max_time = runtime, runtime
                    min_cnfl, max_cnfl = self.conflict_cnt, self.conflict_cnt
                    min_dec, max_dec = self.decision_cnt, self.decision_cnt

                if i != 1:
                    if runtime < min_time:
                        min_time = runtime
                    if runtime > max_time:
                        max_time = runtime
                    if self.conflict_cnt < min_cnfl:
                        min_cnfl = self.conflict_cnt
                    if self.conflict_cnt > max_cnfl:
                        max_cnfl = self.conflict_cnt
                    if self.decision_cnt < min_dec:
                        min_dec = self.decision_cnt
                    if self.decision_cnt > max_dec:
                        max_dec = self.decision_cnt

                f = open(log, 'a')
                fs = open(stat, 'a')
                f.writelines(cnf_folder + '/' + file + '\n')

                if result == SAT:
                    f.writelines('Solution:\n')
                    f.writelines(str(self.assignment_list) + '\n')

                if result == UNSAT:
                    f.writelines('DP Solver finished. Formula UNSAT\n')

                print('--------------------------------')
                if result == SAT:
                    sat_cnt += 1
                    dec_cnt += self.decision_cnt
                    cnfl_cnt += self.conflict_cnt
                    f.writelines('Formula SAT after ' + str(self.decision_cnt) + ' decisions,  ')
                    f.writelines(str(self.split_cnt) + ' splits, ')
                    f.writelines(str(self.conflict_cnt) + ' conflicts. \n')
                    fs.writelines(str(
                        "%3s" % i + ";%15s" % file + ";%9s" % "    SAT" + ";        %.0f" % self.decision_cnt + ";    %.0f" % self.conflict_cnt + ";   %.3f" % runtime + "\n"))
                    print('Formula SAT')
                else:
                    unsat_cnt += 1
                    dec_cnt += self.decision_cnt
                    cnfl_cnt += self.conflict_cnt
                    f.writelines('Formula UNSAT after ' + str(self.decision_cnt) + ' decisions, ')
                    f.writelines(str(self.split_cnt) + ' splits, ')
                    f.writelines(str(self.conflict_cnt) + ' conflicts. \n')
                    fs.writelines(str(
                        "%-3s" % i + ";%-15s" % file + ";%-6s" % "  UNSAT" + ";        %-.0f" % self.decision_cnt + ";    %-.0f" % self.conflict_cnt + ";   %-.3f" % runtime + "\n"))
                    print('Formula UNSAT')
                fs.close()

                print('DPLL SAT Solver version', VERSION)
                print('Execution Time: %.6f seconds' % runtime)

                f.writelines('DPLL SAT Solver version ' + str(VERSION) + '.')
                f.writelines(str(' Execution Time: %.6f ' % runtime + 's' + '\n'))
                f.writelines('\n')
                f.close()

                self.f_list.clear()
                self.v_list.clear()
                self.assignment_list.clear()
                self.assignment_trail.clear()
                self.decision_cnt = 0
                self.split_cnt = 0
                self.conflict_cnt = 0
                self.formula_backtrack_l.clear()
                self.assign_backtrack_l.clear()
                self.decision_backtrack_l.clear()
                i += 1

            f = open(log, 'a')
            f.writelines('Global runtimes for ' + str(i - 1) + ' files in ' + str(cnf_folder) + str(
                ': %.3f' % global_runtime + 's\n'))
            f.writelines('/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ \n')
            f.close()

            avg_dec = dec_cnt / (i - 1)
            avg_cnfl = cnfl_cnt / (i - 1)
            avg_time = global_runtime / (i - 1)

            fg = open(glob, 'a')
            fg.writelines(str(
                "%6s" % test_set + "    3  " + "  %0.f  " % self.var_cnt + "   %.0f   " % self.clause_cnt + "%3s" % sat_cnt + " / %3s" % unsat_cnt + "    %.3f  " % global_runtime + "%.3f" % min_time + " / %.3f" % max_time + " / %.3f" % avg_time + "   %.0f " % min_dec + " / %.0f " % max_dec + " / %.0f " % avg_dec + "   %.0f " % min_cnfl + " / %.0f " % max_cnfl + " / %.0f " % avg_cnfl + '\n'))
            fg.close()

            print('GLOBAL RUNTIME FOR FILES IN ' + cnf_folder + ': %.3f' % global_runtime + 's')

    def run(self):
        self.open_cnf_file(self.cnf_file)
        self.dpll()


if __name__ == '__main__':
    idpll = DpllIteration()
    idpll.test_run()
