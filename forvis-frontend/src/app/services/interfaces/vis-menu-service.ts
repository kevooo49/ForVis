import { InjectionToken } from '@angular/core';
import { Observable } from 'rxjs';
import {SatFile} from "../../model/satFile";

export const VIS_MENU_SERVICE = new InjectionToken<IVisMenuService>('VisMenuService');

export interface IVisMenuService {
    getOverlayStatus(): Observable<any>;

    scheduleTask(fileId: number, visType: string): Observable<any>;

    open(file: SatFile, kind: string): void;

    openConfirmation(file: SatFile, kind: string): void;

    openBadRequest(file: SatFile, kind: string): void;

    close(): void;
}