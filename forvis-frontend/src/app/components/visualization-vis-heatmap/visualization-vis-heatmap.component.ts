import { Component, OnInit, inject, signal, ViewChild, ElementRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Chart, ChartConfiguration, ScatterController, PointElement, LinearScale, Title, Tooltip, Legend } from 'chart.js';
import { CommonModule } from '@angular/common';
import html2canvas from 'html2canvas';

import { FileService } from '../../services/file-service/file.service';
import { AlertService } from '../../services/alert-service/alert.service';
import type { File } from '../../models/file';
import { DownloadableComponent } from '../visualization-download/visualization-download.component';
import { JsonFileService } from '../../services/json-file-service/json-file.service';
import { JSON_FILE_SERVICE, IJsonFileService } from '../../services/interfaces/json-file-service';

// Register the scatter controller and required elements for Chart.js
Chart.register(ScatterController, PointElement, LinearScale, Title, Tooltip, Legend);

interface VisualizationContent {
  datasets: any[];
  options?: any;
}

interface VisualizationData {
  content: VisualizationContent;
}

@Component({
  selector: 'app-visualization-vis-heatmap',
  templateUrl: './visualization-vis-heatmap.component.html',
  styleUrls: ['./visualization-vis-heatmap.component.css'],
  standalone: true,
  imports: [CommonModule],
  providers: [
    { provide: JSON_FILE_SERVICE, useClass: JsonFileService },
    FileService,
    AlertService
  ]
})
export class VisualizationVisHeatmapComponent extends DownloadableComponent implements OnInit {
  @ViewChild('visualization') private visElement!: ElementRef<HTMLCanvasElement>;

  private route = inject(ActivatedRoute);
  private fileService = inject(FileService);
  private alertService = inject(AlertService);
  private jsonFileService = inject(JSON_FILE_SERVICE) as IJsonFileService;

  fileId = signal<number>(0);
  fileName = signal<string>('');
  file = signal<File>({
    id: 0,
    name: '',
    content: null,
    type: '',
    size: 0,
    created_at: '',
    updated_at: '',
    user_id: 0
  });
  info = signal<string | null>(null);
  kind = signal<string>('');

  loading = signal<boolean>(false);

  public visualization: Chart | null = null;
  errorMessage: string | null = null;
  private readonly errorMessageDefault = 'An overload occurred during processing your file. Please try again with other method or file.';

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.fileId.set(params['f']);
      this.fileName.set(params['name']);
      this.kind.set(params['kind']);
      this.loadVis();
    });
  }

  loadVis() {
    this.loading.set(true);
    this.jsonFileService.getJsonFile(this.fileId(), this.kind(), []).subscribe({
      next: (data: any) => {
        console.log('Heatmap backend response:', data);
        this.info.set(null);
        // Accept both {datasets: ...} and {content: {datasets: ...}}
        let content = data && data.datasets ? data : (data && data.content ? data.content : null);
        this.file.set({
          id: this.fileId(),
          name: this.fileName(),
          content: content,
          type: this.kind(),
          size: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          user_id: 0
        });

        // Check for error or empty data
        if (!content || (Array.isArray(content.datasets) && content.datasets.length === 0) || data.error || content.error) {
          this.errorMessage = data.error || (content && content.error) || 'No data available for heatmap visualization.';
          this.loading.set(false);
          return;
        }

        const canvas = this.visElement?.nativeElement;
        if (!canvas) {
          this.alertService.error('Visualization canvas not found');
          return;
        }

        // Destroy existing chart if it exists
        if (this.visualization) {
          this.visualization.destroy();
        }

        const config: ChartConfiguration = {
          type: 'scatter',
          data: {
            datasets: content.datasets
          },
          options: {
            scales: {
              x: {
                type: 'linear',
                position: 'bottom'
              }
            },
            ...(content.options || {})
          }
        };

        this.visualization = new Chart(canvas, config);
        this.errorMessage = null;
        this.loading.set(false);
      },
      error: (error: Error) => {
        this.errorMessage = this.errorMessageDefault;
        this.alertService.error(this.errorMessageDefault);
        console.error('Error loading visualization:', error);
        this.loading.set(false);
      }
    });
  }

  download() {
    // Implementation for downloading the visualization
    const element = document.getElementById('visualization');
    if (element) {
      html2canvas(element).then(canvas => {
        const link = document.createElement('a');
        link.download = 'visualization.png';
        link.href = canvas.toDataURL();
        link.click();
      });
    }
  }
}
