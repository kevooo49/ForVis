import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Subject, Observable } from 'rxjs';
import { Environment } from '../../environments/environment';
import { IVisMenuService } from '../interfaces/vis-menu-service';
import {SatFile} from "../../model/satFile";

@Injectable({
  providedIn: 'root'
})
export class VisMenuService implements IVisMenuService {
  private overlayMenu = new Subject<any>();
  taskUrl: string = `${Environment.baseUrl}/profile/task/`;

  constructor(private http: HttpClient) {}

  getOverlayStatus(): Observable<any> {
    return this.overlayMenu.asObservable();
  }

  scheduleTask(fileId: number, visType: string): Observable<any> {
    const url = `${this.taskUrl}${visType}/${fileId}/`;
    console.log('Scheduling task with URL:', url);
    return this.http.get<any>(url);
  }

  open(file: SatFile, kind: string): void {
    console.log('Opening visualization menu for file:', file, 'kind:', kind);
    this.overlayMenu.next({
      show: true, confirmation: false, badRequest: false, file, kind
    });
  }

  openConfirmation(file: SatFile, kind: string): void {
    console.log('Opening confirmation for file:', file, 'kind:', kind);
    this.overlayMenu.next({
      show: false, confirmation: true, badRequest: false, file, kind
    });
  }

  openBadRequest(file: SatFile, kind: string): void {
    console.log('Opening bad request for file:', file, 'kind:', kind);
    this.overlayMenu.next({
      show: false, confirmation: false, badRequest: true, file, kind
    });
  }

  close(): void {
    console.log('Closing visualization menu');
    this.overlayMenu.next({ show: false, confirmation: false });
  }
}