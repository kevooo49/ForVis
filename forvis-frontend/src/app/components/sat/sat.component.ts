import { Component, Inject, OnInit } from '@angular/core';
import {ALERT_SERVICE, IAlertService} from '../../services/interfaces/alert-service';
import { AUTH_SERVICE, IAuthService } from '../../services/interfaces/auth-service';
import { ModalBadFileComponent } from '../modal-bad-file/modal-bad-file.component';
import { FILE_SERVICE, IFileService } from '../../services/interfaces/file-service';
import { IVisMenuService, VIS_MENU_SERVICE } from '../../services/interfaces/vis-menu-service';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import {FileUploadModule} from "ng2-file-upload";
import {FormsModule} from "@angular/forms";
import {VisMenuComponent} from "../vis-menu/vis-menu.component";
import {NgClass, NgForOf, NgStyle} from "@angular/common";
import {SatFile} from "../../model/satFile";
import { Environment } from '../../environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-sat',
  templateUrl: './sat.component.html',
  imports: [
    FormsModule,
    VisMenuComponent,
    FileUploadModule,
    NgForOf,
    NgStyle,
  ],
  styleUrls: ['./sat.component.css']
})
export class SatComponent implements OnInit {
  files: SatFile[] = [];
  private uploadUrl = `${Environment.baseUrl}/profile/upload/sat/`;
  selectedFiles: File[] = [];
  uploadProgress = 0;
  isUploading = false;

  constructor(
      @Inject(ALERT_SERVICE) private alertService: IAlertService,
      @Inject(FILE_SERVICE) private fileService: IFileService,
      @Inject(VIS_MENU_SERVICE) private visMenuService: IVisMenuService,
      @Inject(AUTH_SERVICE) private authService: IAuthService,
      private modalService: NgbModal,
      private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.updateList();
  }

  // Handle file selection
  onFileSelected(event: any): void {
    const files = event.target.files;
    if (files) {
      this.selectedFiles = Array.from(files);
    }
  }

  // Upload all selected files
  uploadAll(): void {
    if (this.selectedFiles.length === 0) {
      return;
    }

    this.isUploading = true;
    this.uploadProgress = 0;

    // Upload each file sequentially
    this.uploadNextFile(0);
  }

  // Upload a single file and then proceed to the next one
  private uploadNextFile(index: number): void {
    if (index >= this.selectedFiles.length) {
      // All files uploaded
      this.isUploading = false;
      this.selectedFiles = [];
      this.updateList();
      return;
    }

    const file = this.selectedFiles[index];
    this.uploadFile(file).subscribe({
      next: () => {
        // File uploaded successfully, proceed to next file
        this.uploadProgress = ((index + 1) / this.selectedFiles.length) * 100;
        this.uploadNextFile(index + 1);
      },
      error: (error: any) => {
        console.error('Upload error:', error);
        this.modalService.open(ModalBadFileComponent, { centered: true });
        this.isUploading = false;
      }
    });
  }

  // Upload a single file
  private uploadFile(file: File): any {
    const url = `${this.uploadUrl}${file.name}/`;
    console.log('Uploading to URL:', url);
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Get auth token from localStorage directly
    const token = localStorage.getItem('token');
    let headers = new HttpHeaders();
    
    if (token) {
      headers = headers.set('Authorization', 'JWT ' + token);
    }
    
    return this.http.put(url, formData, { headers });
  }

  // Clear selected files
  clearQueue(): void {
    this.selectedFiles = [];
  }

  updateList(): void {
    this.fileService.getSatFilesList().subscribe({
      next: (data: SatFile[]) => this.files = data,
      error: (error: any) => this.alertService.error(error)
    });
  }

  deleteFile(file: SatFile): void {
    this.fileService.deleteSatFile(file.id).subscribe({
      next: () => this.updateList(),
      error: (error: any) => this.alertService.error(error)
    });
  }

  openVisMenu(file: SatFile): void {
    this.visMenuService.open(file, 'sat');
  }
}