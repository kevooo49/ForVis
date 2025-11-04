import { Component, ElementRef, OnInit, ViewChild, Inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DownloadableComponent } from '../visualization-download/visualization-download.component';
import {AUTH_SERVICE, IAuthService} from "../../services/interfaces/auth-service";
import {IJsonFileService, JSON_FILE_SERVICE} from "../../services/interfaces/json-file-service";
import {ALERT_SERVICE, IAlertService} from "../../services/interfaces/alert-service";
import {FILE_SERVICE, IFileService} from "../../services/interfaces/file-service";
import { Chart, CategoryScale, LinearScale, BarController, BarElement, PointElement, LineController, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgSelectModule } from '@ng-select/ng-select';

// Register the required Chart.js components
Chart.register(
  CategoryScale,
  LinearScale,
  BarController,
  BarElement,
  PointElement,
  LineController,
  LineElement,
  Title,
  Tooltip,
  Legend
);

@Component({
    selector: 'app-visualization-vis-distribution',
    templateUrl: './visualization-vis-distribution.component.html',
    styleUrls: ['./visualization-vis-distribution.component.css'],
    standalone: true,
    imports: [CommonModule, FormsModule, NgSelectModule]
})
export class VisualizationVisDistributionComponent extends DownloadableComponent implements OnInit {
    @ViewChild('visualization') private visElement: ElementRef | undefined;

    fileId?: number;
    fileName?: string;
    info: any;
    kind?: string;
    loading: boolean = true;
    numberOfClauses?: number;
    selectedTopPercentage: number = 0;
    selectedChartForm?: string;
    visualization: any;

    topPercentage = [
        { description: "All (100%)", value: 0 },
        { description: "5%", value: 5 },
        { description: "10%", value: 10 },
        { description: "25%", value: 25 },
        { description: "50%", value: 50 },
        { description: "75%", value: 75 }
    ];

    chartForm = [
        { description: "Both", value: "both" },
        { description: "Positive", value: "positive" },
        { description: "Negative", value: "negative" },
        { description: "Only positive/negative variables", value: "singles" }
    ];

    constructor(
        private route: ActivatedRoute,
        @Inject(FILE_SERVICE) private fileService: IFileService,
        @Inject(ALERT_SERVICE) private alertService: IAlertService,
        @Inject(JSON_FILE_SERVICE) private jsonfileService: IJsonFileService,
        @Inject(AUTH_SERVICE) private authService: IAuthService
    ) {
        super();
    }

    ngOnInit() {
        this.route.params.subscribe(
            params => {
                this.fileId = params['f'];
                this.fileName = params['name'];
                this.kind = params['kind'];
                this.loadVis();
            }
        );
    }

    loadVis() {
        if (this.fileId && this.kind) {
            this.jsonfileService.getJsonFile(this.fileId, this.kind, []).subscribe({
                next: (data: { content: { labels: any; negative: any; positive: any; info: any; }; }) => {
                    if (!data?.content?.labels || !data?.content?.negative || !data?.content?.positive) {
                        this.alertService.error('Invalid data structure or missing content.');
                        this.loading = false;
                        return;
                    }

                    this.info = data.content.info;
                    this.numberOfClauses = parseInt(this.info?.[3]?.replace("\n", "") ?? '0');

                    if (isNaN(this.numberOfClauses)) {
                        this.alertService.error('Invalid number of clauses data.');
                        this.loading = false;
                        return;
                    }

                    this.visualization = new Chart('visualization', {
                        type: 'bar',
                        data: {
                            labels: data.content.labels,
                            datasets: [
                                {
                                    label: "Negative",
                                    backgroundColor: "#e63030",
                                    data: data.content.negative
                                },
                                {
                                    label: "Positive",
                                    backgroundColor: "#93eced",
                                    data: data.content.positive
                                }
                            ]
                        },
                        options: {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Distribution of logical variables in formula'
                                }
                            },
                            scales: {
                                x: {
                                    stacked: true,
                                    display: true,
                                    type: 'category',
                                },
                                y: {
                                    stacked: true,
                                    display: true,
                                    type: 'linear'
                                }
                            }
                        }
                    });

                    this.loading = false;
                },
                error: () => {
                    this.alertService.error('Error loading data.');
                    this.loading = false;
                }
            });
        }
    }

    onFilter() {
        if (!this.selectedTopPercentage || !this.selectedChartForm) {
            return;
        }

        if (this.fileId && this.kind) {
            this.jsonfileService.getJsonFile(this.fileId, this.kind, []).subscribe({
                next: (data: { content: { labels: any; negative: any; positive: any; }; }) => {
                    if (!data?.content?.labels || !data?.content?.negative || !data?.content?.positive) {
                        this.alertService.error('Missing or invalid data for filtering.');
                        return;
                    }

                    const labels = [...data.content.labels];
                    let negative = [...data.content.negative];
                    let positive = [...data.content.positive];

                    this.filterChartData(labels, negative, positive);

                    if (this.selectedTopPercentage !== 0) {
                        this.filterTopPercentage(labels, negative, positive);
                    }

                    this.updateChart(labels, negative, positive);
                    this.loading = false;
                },
                error: () => {
                    this.alertService.error('Error while applying filter.');
                    this.loading = false;
                }
            });
        }
    }

    private filterChartData(labels: string[], negative: number[], positive: number[]) {
        switch (this.selectedChartForm) {
            case 'positive':
                negative = [];
                break;
            case 'negative':
                positive = [];
                break;
            case 'singles':
                const newLabels = [];
                const newNegative = [];
                const newPositive = [];
                for (let i = 0; i < labels.length; i++) {
                    if ((positive[i] === 0 && negative[i] > 0) || (negative[i] === 0 && positive[i] > 0)) {
                        newLabels.push(labels[i]);
                        newNegative.push(negative[i]);
                        newPositive.push(positive[i]);
                    }
                }
                labels.length = 0;
                negative.length = 0;
                positive.length = 0;
                labels.push(...newLabels);
                negative.push(...newNegative);
                positive.push(...newPositive);
                break;
        }
    }

    private filterTopPercentage(labels: string[], negative: number[], positive: number[]) {
        const newLabels = [];
        const newNegative = [];
        const newPositive = [];

        const newLabelsLength = Math.floor(parseInt(this.info[2]) * (this.selectedTopPercentage / 100) + 0.99);

        let temp = [...positive, ...negative];
        temp.sort((a, b) => b - a);
        const minimumValue = Math.min(...temp.slice(0, newLabelsLength));

        for (let i = 0; i < labels.length; i++) {
            if (positive[i] + negative[i] >= minimumValue) {
                newLabels.push(labels[i]);
                newNegative.push(negative[i]);
                newPositive.push(positive[i]);
            }
        }

        labels.length = 0;
        negative.length = 0;
        positive.length = 0;
        labels.push(...newLabels);
        negative.push(...newNegative);
        positive.push(...newPositive);
    }

    private updateChart(labels: string[], negative: number[], positive: number[]) {
        if (this.visualization) {
            this.visualization.data.datasets = [
                { label: "Negative", backgroundColor: "#e63030", data: negative },
                { label: "Positive", backgroundColor: "#93eced", data: positive }
            ];
            this.visualization.data.labels = labels;
            this.visualization.update();
        }
    }
}