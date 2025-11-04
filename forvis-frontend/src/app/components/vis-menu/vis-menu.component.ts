import {Component, Inject, OnInit} from '@angular/core';
import { Router } from '@angular/router';
import {IVisMenuService, VIS_MENU_SERVICE} from "../../services/interfaces/vis-menu-service";
import {SatFile} from "../../model/satFile";
import {NgIf} from "@angular/common";

@Component({
  selector: 'app-vis-menu',
  templateUrl: './vis-menu.component.html',
  imports: [
    NgIf
  ],
  styleUrls: ['./vis-menu.component.css']
})
export class VisMenuComponent implements OnInit {
  showMenu = false;
  showConfirmation = false;
  showBadRequest = false;
  file: SatFile | undefined;
  kind: string | undefined;
  taskMessage: string | undefined;

  constructor(
      @Inject(VIS_MENU_SERVICE) private visMenuService: IVisMenuService,
      private router: Router
  ) {}

  ngOnInit() {
    console.log('VisMenuComponent initialized');
    this.visMenuService.getOverlayStatus().subscribe(data => {
      console.log('Received overlay status:', data);
      this.showMenu = data.show;
      this.file = data.file;
      this.kind = data.kind;
      this.showConfirmation = data.confirmation;
      this.showBadRequest = data.badRequest;
    });
  }

  visualizeFile(visType: string) {
    if (!this.file) {
      console.error('No file selected for visualization');
      return;
    }
    
    console.log('Visualizing file:', this.file, 'with type:', visType);
    let type = visType !== 'raw' ? `${this.kind}_${visType}` : visType;

    this.visMenuService.scheduleTask((this.file as any).id, type).subscribe({
      next: (data: any) => {
        console.log('Task scheduled successfully:', data);
        this.taskMessage = data.message;

        if (data.status === 'ok') {
          this.confirm();
        } else {
          this.badRequest();
        }
      },
      error: (err) => {
        console.error('Error scheduling task:', err);
        this.taskMessage = 'Error scheduling task: ' + err.message;
        this.badRequest();
      }
    });
  }

  confirm() {
    if (this.file && this.kind) {
      console.log('Confirming visualization for file:', this.file, 'kind:', this.kind);
      this.visMenuService.openConfirmation(this.file, this.kind);
    }
  }

  badRequest() {
    if (this.file && this.kind) {
      console.log('Bad request for file:', this.file, 'kind:', this.kind);
      this.visMenuService.openBadRequest(this.file, this.kind);
    }
  }

  close() {
    console.log('Closing visualization menu');
    this.visMenuService.close();
  }
}