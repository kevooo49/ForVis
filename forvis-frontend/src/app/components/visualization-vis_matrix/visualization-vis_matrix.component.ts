import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';

import { FileService } from '../../services/file-service/file.service';
import { AlertService } from '../../services/alert-service/alert.service';
import type { File } from '../../models/file';
import { JsonFileService } from '../../services/json-file-service/json-file.service';
import { JSON_FILE_SERVICE } from '../../services/interfaces/json-file-service';
import { ALERT_SERVICE } from '../../services/interfaces/alert-service';
import { FILE_SERVICE } from '../../services/interfaces/file-service';

class FormulaDependency {
    public positive: number = 0;
    public negative: number = 0;
}

class DependencyRow {
    public dependencies: FormulaDependency[] = [];
}

class DependencyMatrix {
    public labels: string[] = [];
    public rows: DependencyRow[] = [];
}

@Component({
  selector: 'app-visualization-vis_matrix',
  templateUrl: './visualization-vis_matrix.component.html',
  styleUrls: ['./visualization-vis_matrix.component.css'],
  standalone: true,
  imports: [CommonModule],
  providers: [
    { provide: JSON_FILE_SERVICE, useClass: JsonFileService },
    { provide: ALERT_SERVICE, useClass: AlertService },
    { provide: FILE_SERVICE, useClass: FileService }
  ]
})
export class VisualizationVisMatrixComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private fileService = inject(FileService);
  private alertService = inject(AlertService);
  private jsonFileService = inject(JSON_FILE_SERVICE);

  readonly redCellStyle = {'background-color': 'hsl(0, 65%, 62%)'};
  readonly greenCellStyle = {'background-color': 'hsl(101, 65%, 62%)'};
  readonly yellowCellStyle = {'background-color': 'hsl(54, 65%, 62%)'};

  fileId = signal<number>(0);
  fileName = signal<string>('');
  info = signal<string | null>(null);
  kind = signal<string>('');

  loading = signal<boolean>(true);
  colorsOn = signal<boolean>(false);

  selectedMode = signal<number>(0);

  public matrix = signal<DependencyMatrix | null>(null);

  private readonly errorMessage = 'An overload occurred during processing your file. Please try again with other method or file.';

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.fileId.set(params['f']);
      this.fileName.set(params['name']);
      this.kind.set(params['kind']);
      this.loadVis();
    });
  }

  private getCellStyle0(dependency: FormulaDependency) {
    if (dependency.positive + dependency.negative != 0)
      return this.yellowCellStyle;
    return {};
  }

  private getCellStyle1(dependency: FormulaDependency) {
    if (dependency.positive > 0) {
      if (dependency.negative > 0) {
        return this.yellowCellStyle;
      } else {
        return this.greenCellStyle;
      }
    }
    if (dependency.negative > 0) {
      return this.redCellStyle;
    }
    return {};
  }

  private getCellStyle2(dependency: FormulaDependency) {
    if (dependency.negative == dependency.positive) {
      return dependency.negative == 0 ? {} : this.yellowCellStyle;
    } else if (dependency.negative < dependency.positive) {
      return this.greenCellStyle;
    } else {
      return this.redCellStyle;
    }
  }

  getCellStyle(dependency: FormulaDependency, rowIndx: number, colIndx: number) {
    if (rowIndx == colIndx) {
      return {'background-color': "#000000"};
    }

    if (!this.colorsOn())
      return {};

    if (this.selectedMode() == 0)
      return this.getCellStyle0(dependency);

    if (this.selectedMode() == 1)
      return this.getCellStyle1(dependency);

    if (this.selectedMode() == 2)
      return this.getCellStyle2(dependency);
    
    return {};
  }

  getCellContent(dependency: FormulaDependency) {
    if (this.selectedMode() == 0) {
      return dependency.positive + dependency.negative != 0 ? "x" : " ";
    }
    if (this.selectedMode() == 1) {
      let out = dependency.positive > 0 ? "+" : "";
      if (dependency.negative > 0)
        out += dependency.positive > 0 ? "/-" : "-";
      return out;
    } else {
      return dependency.positive + "/" + dependency.negative;
    }
  }

  selectMode(nr: number) {
    this.selectedMode.set(nr);
  }

  getColorButtonText() {
    if (this.colorsOn())
      return "Disable colors";
    else
      return "Enable colors";
  }

  switchColors() {
    this.colorsOn.set(!this.colorsOn());
  }

  loadVis() {
    this.jsonFileService.getJsonFile(this.fileId(), this.kind(), []).subscribe({
      next: (data: any) => {
        const matrix = new DependencyMatrix();
        matrix.labels = data.content.labels;
        matrix.rows = data.content.rows;
        this.matrix.set(matrix);
        this.loading.set(false);
      },
      error: (error: Error) => {
        this.alertService.error(this.errorMessage);
        console.error('Error loading visualization:', error);
      }
    });
  }
}
