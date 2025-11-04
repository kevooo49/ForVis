import {Component, Inject, OnInit} from '@angular/core';
import {FileUploader, FileUploadModule} from 'ng2-file-upload';
import {ModalBadFileComponent} from '../modal-bad-file/modal-bad-file.component';
import {NgbModal} from '@ng-bootstrap/ng-bootstrap';
import {ALERT_SERVICE, IAlertService} from "../../services/interfaces/alert-service";
import {FILE_SERVICE, IFileService} from "../../services/interfaces/file-service";
import {IVisMenuService, VIS_MENU_SERVICE} from "../../services/interfaces/vis-menu-service";
import {IAuthService} from "../../services/interfaces/auth-service";
import {SatFile} from "../../model/satFile";
import {NgForOf, NgIf, NgStyle} from "@angular/common";
import {VisMenuComponent} from "../vis-menu/vis-menu.component";

@Component({
  selector: 'app-max-sat',
  templateUrl: './max-sat.component.html',
  imports: [
    FileUploadModule,
    NgStyle,
    NgForOf,
    VisMenuComponent,
    NgIf
  ],
  styleUrls: ['./max-sat.component.css']
})
export class MaxSatComponent implements OnInit {
  public uploader: FileUploader;

  files: Array<SatFile> = [];

  constructor(
      @Inject(ALERT_SERVICE) private alertService: IAlertService,
      @Inject(FILE_SERVICE) private fileService: IFileService,
      @Inject(VIS_MENU_SERVICE) private visMenuService: IVisMenuService,
      @Inject(ALERT_SERVICE) private authService: IAuthService,
      private modalService: NgbModal
  ) {
    this.uploader = new FileUploader({
      url: 'about:blank'
    });
  }

  ngOnInit() {
    this.updateList();

    this.uploader.authToken = this.authService.getAuthTokenString() ?? undefined;
    this.uploader.onBeforeUploadItem = (item) => {
      item.method = 'PUT';
      item.url = '/api/profile/upload/sat/' + item.file.name + '/';
    };

    this.uploader.onSuccessItem = (item:any, response:any, status:any, headers:any) => {
      this.updateList();

      setTimeout(() => {
          this.updateList();
        },
        8000
      );
      this.uploader.clearQueue();
    };
    this.uploader.onErrorItem = (item, response, status, headers) => {
      const modalRef = this.modalService.open(ModalBadFileComponent, {
        centered: true,
      });
      this.uploader.clearQueue();
    };
  }

  updateList(){
    this.fileService.getMaxSatFilesList().subscribe({
      next: data => this.files = data,
      error: error => this.alertService.error(error),
    });
  }

  deleteFile(file: SatFile){
    this.fileService.deleteSatFile(file.id).subscribe({
      next: data => this.updateList(),
      error: error => this.alertService.error(error),
    });
  }

  openVisMenu(file: SatFile){
    this.visMenuService.open(file, 'maxsat');
  }
}
