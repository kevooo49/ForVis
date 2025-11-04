import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Network, Node, Edge } from 'vis-network';
import { DataSet } from 'vis-data';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { FileService } from '../../services/file-service/file.service';
import { AlertService } from '../../services/alert-service/alert.service';
import type { File } from '../../models/file';
import { DownloadableComponent } from '../visualization-download/visualization-download.component';
import { JsonFileService } from '../../services/json-file-service/json-file.service';
import { JSON_FILE_SERVICE } from '../../services/interfaces/json-file-service';
import { ALERT_SERVICE } from '../../services/interfaces/alert-service';
import { FILE_SERVICE } from '../../services/interfaces/file-service';

interface VisualizationContent {
  nodes: Node[];
  edges: Edge[];
  variables: string[];
  options: any;
}

interface VisualizationData {
  content: VisualizationContent;
}

interface Font {
  size: number;
  [key: string]: any;
}

@Component({
  selector: 'app-visualization-vis_resolution',
  templateUrl: './visualization-vis_resolution.component.html',
  styleUrls: ['./visualization-vis_resolution.component.css'],
  standalone: true,
  imports: [CommonModule, FormsModule],
  providers: [
    { provide: JSON_FILE_SERVICE, useClass: JsonFileService },
    { provide: ALERT_SERVICE, useClass: AlertService },
    { provide: FILE_SERVICE, useClass: FileService }
  ]
})
export class VisualizationVisResolutionComponent extends DownloadableComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private fileService = inject(FileService);
  private alertService = inject(AlertService);
  private jsonFileService = inject(JSON_FILE_SERVICE);

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
  stabilizationInProgress = signal<boolean>(false);
  isLoaded = signal<boolean>(false);

  public nodes: DataSet<Node> | null = null;
  public edges: DataSet<Edge> | null = null;
  public override network: Network | null = null;

  public variables = signal<string[]>([]);
  public selectedVariables = signal<string[]>([]);
  isSelectAll = signal<boolean>(true);

  private readonly errorMessage = 'An overload occurred during processing your file. Please try again with other method or file.';

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.fileId.set(params['f']);
      this.fileName.set(params['name']);
      this.kind.set(params['kind']);
      this.loadVis();
    });
  }

  startStab() {
    if (this.network) {
      this.network.startSimulation();
    }
  }

  stopStab() {
    if (this.network) {
      this.network.stopSimulation();
      this.network.fit();
    }
  }

  loadFileVariables() {
    const getFile = this.kind() === 'sat' 
      ? this.fileService.getSatFile(this.fileId(), 'variables')
      : this.fileService.getMaxSatFile(this.fileId(), 'variables');

    getFile.subscribe({
      next: (data: any) => {
        if (data['content']['data']['message']) {
          setTimeout(() => {
            this.loadFileVariables();
          }, 1000);
        } else {
          this.variables.set(data['content']['data']['variables']);
        }
      },
      error: (error: Error) => {
        this.alertService.error('Error loading variables');
        console.error('Error loading variables:', error);
      }
    });
  }

  loadVis(selectedVars: string[] = []) {
    this.jsonFileService.getJsonFile(this.fileId(), this.kind(), selectedVars).subscribe({
      next: (data: VisualizationData) => {
        this.info.set(null);
        this.file.set({
          id: this.fileId(),
          name: this.fileName(),
          content: data.content,
          type: this.kind(),
          size: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          user_id: 0
        });

        this.variables.set(data.content.variables);
        this.nodes = new DataSet(data.content.nodes);
        this.edges = new DataSet(data.content.edges);

        this.nodes.forEach((node: Node) => {
          const font = node.font as Font;
          if (font && font.size < 1) {
            font.size = 1;
          }
        });

        const container = document.getElementById('visualization');
        if (!container) {
          this.alertService.error('Visualization container not found');
          return;
        }

        const _data = {
          nodes: this.nodes,
          edges: this.edges
        };

        const options = {
          edges: {
            smooth: false
          },
          physics: {
            enabled: true,
            barnesHut: {
              avoidOverlap: 1,
              centralGravity: 10
            },
            maxVelocity: 1,
            minVelocity: 1,
            timestep: 0.1
          }
        };

        this.loading.set(true);
        this.network = new Network(container, _data, options);
        this.stopStab();

        if (this.network) {
          this.network.on('startStabilizing', () => {
            this.stabilizationInProgress.set(true);
          });

          this.network.on('stabilized', () => {
            this.stabilizationInProgress.set(false);
          });

          this.network.once('stabilizationIterationsDone', () => {
            this.loading.set(false);
            this.isLoaded.set(true);
            this.stabilizationInProgress.set(false);
          });
        }
      },
      error: (error: Error) => {
        this.alertService.error(this.errorMessage);
        console.error('Error loading visualization:', error);
      }
    });
  }

  onDraw() {
    this.loading.set(true);
    if (!this.isSelectAll() && this.selectedVariables().length > 0) {
      this.loadVis(this.selectedVariables());
    } else {
      this.loadVis();
    }
  }
}
