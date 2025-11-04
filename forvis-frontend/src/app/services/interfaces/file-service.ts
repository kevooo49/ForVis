import {InjectionToken} from "@angular/core";
import {Observable} from "rxjs";

export const FILE_SERVICE = new InjectionToken<IFileService>('FileService');

export interface IFileService {
    getSatFilesList(): Observable<any>;

    getSatFile(id: number, format: string, selectedVariables: string[]): Observable<any>;

    deleteSatFile(id: number): Observable<any>;

    getMaxSatFilesList(): Observable<any>;

    getMaxSatFile(id: number, format: string, selectedVariables: string[]): Observable<any>;

    deleteMaxSatFile(id: number): Observable<any>;
}
