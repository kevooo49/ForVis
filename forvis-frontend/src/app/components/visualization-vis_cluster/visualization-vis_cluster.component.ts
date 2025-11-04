import { Component, OnInit, inject, signal, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Network, Node as VisNode, Edge } from 'vis-network';
import { DataSet } from 'vis-data';
import { CommonModule } from '@angular/common';
import html2canvas from 'html2canvas';

import { FileService } from '../../services/file-service/file.service';
import { AlertService } from '../../services/alert-service/alert.service';
import type { File } from '../../models/file';
import { DownloadableComponent } from '../visualization-download/visualization-download.component';
import { JsonFileService } from '../../services/json-file-service/json-file.service';
import { JSON_FILE_SERVICE } from '../../services/interfaces/json-file-service';
import { ALERT_SERVICE } from '../../services/interfaces/alert-service';
import { FILE_SERVICE } from '../../services/interfaces/file-service';

interface Node extends VisNode {
  cluster?: string;
}

interface VisualizationContent {
  clusteredNetwork: {
    nodes: Node[];
    edges: Edge[];
  };
  wholeNetwork: {
    nodes: Node[];
    edges: Edge[];
  };
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
  selector: 'app-visualization-vis_cluster',
  templateUrl: './visualization-vis_cluster.component.html',
  styleUrls: ['./visualization-vis_cluster.component.css'],
  standalone: true,
  imports: [CommonModule],
  providers: [
    { provide: JSON_FILE_SERVICE, useClass: JsonFileService },
    { provide: ALERT_SERVICE, useClass: AlertService },
    { provide: FILE_SERVICE, useClass: FileService }
  ]
})
export class VisualizationVisClusterComponent extends DownloadableComponent implements OnInit, AfterViewInit {
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
  selectedCluster = signal<string | null>(null);

  loading = signal<boolean>(false);

  public nodesC: DataSet<Node> | null = null;
  public edgesC: DataSet<Edge> | null = null;
  public nodesW: DataSet<Node> | null = null;
  public edgesW: DataSet<Edge> | null = null;

  public clusteredNetwork: Network | null = null;
  public zoomedNetwork: Network | null = null;
  public override network: Network | null = null;

  private readonly errorMessage = 'An overload occurred during processing your file. Please try again with other method or file.';

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.fileId.set(params['f']);
      this.fileName.set(params['name']);
      this.kind.set(params['kind']);
      this.loadVis();
    });
  }

  ngAfterViewInit() {
    const zoomContainer = document.getElementById('zoom');
    if (zoomContainer) {
      zoomContainer.style.display = 'block';
    }
  }

  private zoomOnSelectedCluster = (selectNodeEvent: { nodes: string[] }) => {
    if (!selectNodeEvent.nodes.length) return;

    this.selectedCluster.set(`Cluster ${selectNodeEvent.nodes[0]}`);

    if (this.zoomedNetwork) {
      this.zoomedNetwork.destroy();
    }

    const clusterId = selectNodeEvent.nodes[0];
    const containerZoom = document.getElementById('zoom');
    if (!containerZoom) return;

    const nodes = this.nodesW?.get().filter(node => node.cluster === clusterId) || [];

    const edges = this.edgesW?.get().filter(edge => {
      const node1 = this.nodesW?.get().find(node => node.id === edge.from);
      const node2 = this.nodesW?.get().find(node => node.id === edge.to);
      return node1?.cluster === clusterId && node2?.cluster === clusterId;
    }) || [];

    if (nodes.length === 0) {
      containerZoom.innerHTML = '<div class="empty-cluster">No nodes found in this cluster</div>';
      return;
    }

    const data = {
      nodes: new DataSet(nodes),
      edges: new DataSet(edges)
    };

    const options = {
      ...this._networkOptions,
      physics: {
        enabled: true,
        stabilization: {
          iterations: 100
        }
      }
    };

    this.zoomedNetwork = new Network(containerZoom, data, options);

    this.zoomedNetwork.on("stabilizationIterationsDone", () => {
      this.zoomedNetwork?.setOptions({ physics: { enabled: false } });
    });
  };

  private zoomOnSelectedEdge = (selectEdgeEvent: { edges: string[] }) => {
    if (!selectEdgeEvent.edges.length) return;

    if (this.zoomedNetwork) {
      this.zoomedNetwork.destroy();
    }

    const selectedEdge = this.edgesC?.get().find(edge => edge.id === selectEdgeEvent.edges[0]);
    if (!selectedEdge) return;

    this.selectedCluster.set(`Connection between Cluster ${selectedEdge.from} and Cluster ${selectedEdge.to}`);

    const cluster1Id = selectedEdge.from;
    const cluster2Id = selectedEdge.to;
    const containerZoom = document.getElementById('zoom');
    if (!containerZoom) return;

    const edgesBetweenClusters = this.edgesW?.get().filter(edge => {
      const node1 = this.nodesW?.get().find(node => node.id === edge.from);
      const node2 = this.nodesW?.get().find(node => node.id === edge.to);
      return (node1?.cluster === cluster1Id && node2?.cluster === cluster2Id) ||
          (node1?.cluster === cluster2Id && node2?.cluster === cluster1Id);
    }) || [];

    const nodesSet = new Set<string | number>();

    edgesBetweenClusters.forEach(edge => {
      if (edge.from !== undefined) {
        nodesSet.add(edge.from);
      }
      if (edge.to !== undefined) {
        nodesSet.add(edge.to);
      }
    });


    const nodes = this.nodesW?.get().filter(node => nodesSet.has(node.id)) || [];

    if (nodes.length === 0) {
      containerZoom.innerHTML = '<div class="empty-cluster">No connections found between these clusters</div>';
      return;
    }

    const data = {
      nodes: new DataSet(nodes),
      edges: new DataSet(edgesBetweenClusters)
    };

    const options = {
      ...this._networkOptions,
      physics: {
        enabled: true,
        stabilization: {
          iterations: 100
        }
      }
    };

    this.zoomedNetwork = new Network(containerZoom, data, options);

    this.zoomedNetwork.on("stabilizationIterationsDone", () => {
      this.zoomedNetwork?.setOptions({ physics: { enabled: false } });
    });
  };

  private _networkOptions = {
    nodes: {
      shape: 'dot',
      size: 10,
      font: {
        size: 12,
        face: 'Tahoma'
      },
      borderWidth: 2
    },
    edges: {
      width: 1,
      smooth: false
    },
    interaction: {
      hover: true,
      selectConnectedEdges: true,
      multiselect: false,
      dragNodes: true,
      zoomView: true
    },
    physics: {
      enabled: false
    }
  };

  loadVis() {
    this.loading.set(true);
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

        this.nodesC = new DataSet(data.content.clusteredNetwork.nodes);
        this.edgesC = new DataSet(data.content.clusteredNetwork.edges);
        this.nodesW = new DataSet(data.content.wholeNetwork.nodes);
        this.edgesW = new DataSet(data.content.wholeNetwork.edges);

        this.nodesC.forEach((node: Node) => {
          const font = node.font as Font;
          if (font && font.size < 1) {
            font.size = 14; // More readable size
          }
        });

        this.nodesW.forEach((node: Node) => {
          const font = node.font as Font;
          if (font && font.size < 1) {
            font.size = 12; // Standard size
          }
        });

        const containerMain = document.getElementById('visualization');
        if (!containerMain) {
          this.alertService.error('Visualization container not found');
          return;
        }

        const _dataC = {
          nodes: this.nodesC,
          edges: this.edgesC
        };

        const clusterOptions = {
          ...this._networkOptions,
          nodes: {
            ...this._networkOptions.nodes,
            size: 30
          }
        };

        this.clusteredNetwork = new Network(containerMain, _dataC, clusterOptions);
        this.clusteredNetwork.on("selectNode", this.zoomOnSelectedCluster);
        this.clusteredNetwork.on("selectEdge", this.zoomOnSelectedEdge);
        this.clusteredNetwork.on("deselectNode", () => {
          this.selectedCluster.set(null);
        });
        this.clusteredNetwork.on("deselectEdge", () => {
          this.selectedCluster.set(null);
        });

        this.network = this.clusteredNetwork;

        this.loading.set(false);

        const zoomDiv = document.getElementById('zoom');
        if (zoomDiv) {
          zoomDiv.innerHTML = '<div class="cluster-info">Click on a cluster or edge in the graph above to see its details here</div>';
        }
      },
      error: (error: Error) => {
        this.alertService.error(this.errorMessage);
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