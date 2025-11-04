import {Component, Inject, OnInit} from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import { Network, Node, Edge } from 'vis-network';
import { DataSet } from 'vis-data';
import { DownloadableComponent } from '../visualization-download/visualization-download.component';
import {FILE_SERVICE, IFileService} from "../../services/interfaces/file-service";
import {ALERT_SERVICE, IAlertService} from "../../services/interfaces/alert-service";
import {IJsonFileService, JSON_FILE_SERVICE} from "../../services/interfaces/json-file-service";
import {SatFile} from "../../model/satFile";
import {NgIf} from "@angular/common";

@Component({
    selector: 'app-visualization-vis-community',
    templateUrl: './visualization-vis-community.component.html',
    imports: [
        NgIf
    ],
    styleUrls: ['./visualization-vis-community.component.css']
})
export class VisualizationVisCommunityComponent extends DownloadableComponent implements OnInit {
  fileId?: number;
  fileName?: string;
  file: SatFile = {
        id: 0,
        name: ''
    };
  info?: string;
  kind?: string;
  loading?: boolean;
  stabilizationInProgress?: boolean;

    public nodes?: DataSet<Node>;
    public edges?: DataSet<Edge>;

    constructor(
    private route: ActivatedRoute,
    @Inject(FILE_SERVICE) private fileService: IFileService,
    @Inject(ALERT_SERVICE) private alertService: IAlertService,
    @Inject(JSON_FILE_SERVICE) private jsonfileService: IJsonFileService,
  ) { super() }

  ngOnInit() {
    this.route.params.subscribe(
      params => {
         this.fileId = params['f'];
         this.fileName = params['name'];
         this.kind = params['kind'];
         this.loadVis();
    });
  }

  startStab(){
      if (this.network) {
          this.network.startSimulation();
      }
  }

  stopStab(){
      if (this.network) {
          this.network.stopSimulation();
          this.network.fit();
      }
  }

    loadVis() {
        if (this.fileId && this.fileName && this.kind) {
            this.jsonfileService.getJsonFile(this.fileId, this.kind, []).subscribe({
                next: data => {
                    this.info = undefined;
                    this.file = data;

                    this.nodes = new DataSet<Node>(data.content.nodes);
                    this.edges = new DataSet<Edge>(data.content.edges);

                    this.nodes.forEach(node => {
                        if (node.font && typeof node.font === 'object' && node.font.size && node.font.size < 1) {
                            node.font.size = 1;
                        }
                    });

                    const container = document.getElementById('visualization');
                    if (!container) {
                        console.error("Visualization container not found.");
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
                                centralGravity: 3.5
                            },
                            maxVelocity: 1,
                            minVelocity: 1
                        }
                    };

                    this.loading = true;
                    this.network = new Network(container, _data, options);
                    this.stopStab();

                    this.network.on("startStabilizing", () => {
                        this.stabilizationInProgress = true;
                    });

                    this.network.on("stabilized", () => {
                        this.stabilizationInProgress = false;
                    });

                    this.network.once("stabilizationIterationsDone", () => {
                        this.loading = false;
                        this.stabilizationInProgress = false;
                    });
                },
                error: err => {
                    this.alertService.error('Failed to load visualization');
                    console.error(err);
                }
            });
        }
    }
}
