import {Component, Inject, OnInit} from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import {FILE_SERVICE, IFileService} from "../../services/interfaces/file-service";
import {ALERT_SERVICE, IAlertService} from "../../services/interfaces/alert-service";
import {IJsonFileService, JSON_FILE_SERVICE} from "../../services/interfaces/json-file-service";
import {SatFile} from "../../model/satFile";
import {NgIf} from "@angular/common";

@Component({
    selector: 'app-visualization-raw',
    templateUrl: './visualization-raw.component.html',
    imports: [
        NgIf
    ],
    styleUrls: ['./visualization-raw.component.css']
})
export class VisualizationRawComponent implements OnInit {
  fileId?: number;
  fileName?: string;
  file: SatFile = {
      id: 0,
      name: ''
  }
  info?: string;
  kind?: string;
  file_content?: string;

  constructor(
    private route: ActivatedRoute,
    @Inject(FILE_SERVICE) private fileService: IFileService,
    @Inject(ALERT_SERVICE) private alertService: IAlertService,
    @Inject(JSON_FILE_SERVICE) private jsonfileService: IJsonFileService,
  ) { }

  ngOnInit() {
    this.route.params.subscribe(
      params => {
         this.fileId = params['f'];
         this.fileName = params['name'];
         this.kind = params['kind'];
         this.loadVis();
    });
  }

  loadVis() {
      if (this.fileId && this.fileName && this.kind) {
          this.jsonfileService.getJsonFile(this.fileId, this.kind, []).subscribe(
              data => {
                  this.file_content = data.content.raw;
                  console.log(this.file_content);
              }
          )
      }
  };
}

