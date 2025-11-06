import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { AccountEditComponent } from './components/account-edit/account-edit.component';
import { DocsComponent } from './components/docs/docs.component';
import { SatComponent } from './components/sat/sat.component';
import { MaxSatComponent } from './components/max-sat/max-sat.component';
import { VisualizationsComponent } from './components/visualizations/visualizations.component';
import { VisualizationVis2ClauseComponent } from './components/visualization-vis_2clause/visualization-vis_2clause.component';
import { VisualizationVisFactorComponent } from './components/visualization-vis_factor/visualization-vis_factor.component';
import { VisualizationVisInteractionComponent } from './components/visualization-vis_interaction/visualization-vis_interaction.component';
import { VisualizationVisMatrixComponent } from './components/visualization-vis_matrix/visualization-vis_matrix.component';
import { VisualizationVisTreeComponent } from './components/visualization-vis_tree/visualization-vis_tree.component';
import { VisualizationVisClusterComponent } from './components/visualization-vis_cluster/visualization-vis_cluster.component';
import { VisualizationVisResolutionComponent } from './components/visualization-vis_resolution/visualization-vis_resolution.component';
import { VisualizationVisDistributionComponent } from './components/visualization-vis-distribution/visualization-vis-distribution.component';
import { VisualizationVisDirectedComponent } from './components/visualization-vis_directed/visualization-vis_directed.component';
import { VisualizationVisDpllComponent } from './components/visualization-vis_dpll/visualization-vis_dpll.component';
import { VisualizationVisHeatmapComponent } from './components/visualization-vis-heatmap/visualization-vis-heatmap.component';
import { VisualizationRawComponent } from './components/visualization-raw/visualization-raw.component';
import { VisualizationVisCommunityComponent } from './components/visualization-vis-community/visualization-vis-community.component';
import {CnfUploader} from "./components/cnf-uploader/cnf-uploader";
import { AuthGuard } from './guards/auth.guard';


export const routes: Routes = [
  { path: 'home', component: HomeComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'account', component: AccountEditComponent },
  { path: 'docs', component: DocsComponent },
  { path: 'sat', component: SatComponent, canActivate: [AuthGuard] },
  // { path: 'sat', component: SatComponent },
  { path: 'max-sat', component: MaxSatComponent, canActivate: [AuthGuard] },
  { path: 'visualizations', component: VisualizationsComponent },
  { path: 'visualization-vis_2clause/:f/:name/:kind', component: VisualizationVis2ClauseComponent },
  { path: 'visualization-vis_factor/:f/:name/:kind', component: VisualizationVisFactorComponent },
  { path: 'visualization-vis_interaction/:f/:name/:kind', component: VisualizationVisInteractionComponent },
  { path: 'visualization-vis_matrix/:f/:name/:kind', component: VisualizationVisMatrixComponent },
  { path: 'visualization-vis_tree/:f/:name/:kind', component: VisualizationVisTreeComponent },
  { path: 'visualization-vis_cluster/:f/:name/:kind', component: VisualizationVisClusterComponent },
  { path: 'visualization-vis_resolution/:f/:name/:kind', component: VisualizationVisResolutionComponent },
  { path: 'visualization-vis_distribution/:f/:name/:kind', component: VisualizationVisDistributionComponent },
  { path: 'visualization-vis_directed/:f/:name/:kind', component: VisualizationVisDirectedComponent },
  { path: 'visualization-vis_dpll/:f/:name/:kind', component: VisualizationVisDpllComponent },
  { path: 'visualization-vis-heatmap/:f/:name/:kind', component: VisualizationVisHeatmapComponent },
  { path: 'visualization-raw/:f/:name/:kind', component: VisualizationRawComponent },
  { path: 'visualization-vis-community/:f/:name/:kind', component: VisualizationVisCommunityComponent },
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'cnf-uploader', component: CnfUploader },
  // { path: '**', redirectTo: 'login' },
  { path: '**', redirectTo: '/home' }
];