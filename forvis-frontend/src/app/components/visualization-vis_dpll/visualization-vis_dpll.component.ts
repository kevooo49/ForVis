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
  options: any;
  dlis_nodes?: Node[];
  dlis_edges?: Edge[];
  jw_nodes?: Node[];
  jw_edges?: Edge[];
  moms_nodes?: Node[];
  moms_edges?: Edge[];
}

interface VisualizationData {
  content: VisualizationContent;
}

interface Font {
  size: number;
  [key: string]: any;
}

@Component({
  selector: 'app-visualization-vis_dpll',
  templateUrl: './visualization-vis_dpll.component.html',
  styleUrls: ['./visualization-vis_dpll.component.css'],
  standalone: true,
  imports: [CommonModule, FormsModule],
  providers: [
    { provide: JSON_FILE_SERVICE, useClass: JsonFileService },
    { provide: ALERT_SERVICE, useClass: AlertService },
    { provide: FILE_SERVICE, useClass: FileService }
  ]
})
export class VisualizationVisDpllComponent extends DownloadableComponent implements OnInit {
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

  public nodes: DataSet<Node> | null = null;
  public edges: DataSet<Edge> | null = null;
  public override network: Network | null = null;

  heuristicType = signal<number>(3);

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

  loadVis(heuType = 3) {
    this.jsonFileService.getJsonFile(this.fileId(), this.kind(), []).subscribe({
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

        if (heuType === 1 && data.content.dlis_nodes && data.content.dlis_edges) {
          this.nodes = new DataSet(data.content.dlis_nodes);
          this.edges = new DataSet(data.content.dlis_edges);
        } else if (heuType === 2 && data.content.jw_nodes && data.content.jw_edges) {
          this.nodes = new DataSet(data.content.jw_nodes);
          this.edges = new DataSet(data.content.jw_edges);
        } else if (data.content.moms_nodes && data.content.moms_edges) {
          this.nodes = new DataSet(data.content.moms_nodes);
          this.edges = new DataSet(data.content.moms_edges);
        } else {
          this.alertService.error('Selected heuristic data not available');
          return;
        }
        
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
        
        const options = data.content.options || {
          edges: {
            smooth: false
          },
          physics: {
            enabled: true,
            barnesHut: {
              avoidOverlap: 1
            },
            maxVelocity: 1,
            minVelocity: 1
          }
        };
        
        this.loading.set(true);
        this.network = new Network(container, _data, options);
        this.stopStab();

        if (this.network) {
          this.network.on("startStabilizing", () => {
            this.stabilizationInProgress.set(true);
          });

          this.network.on("stabilized", () => {
            this.stabilizationInProgress.set(false);
          });

          this.network.once("stabilizationIterationsDone", () => {
            this.loading.set(false);
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

  loadHeuristic() {
    this.loading.set(true);
    this.loadVis(this.heuristicType());
  }
}
