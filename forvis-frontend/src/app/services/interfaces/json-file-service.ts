import {InjectionToken} from '@angular/core';
import {User} from '../../model/user';
import {Observable} from 'rxjs';
import {Jsonfile} from "../../model/jsonFile";

export const JSON_FILE_SERVICE = new InjectionToken<IJsonFileService>('JsonFileService');

export interface IJsonFileService {
    visualizeCommunity(vis: Jsonfile): void;

    getJsonFileList(): Observable<any>;

    getJsonFile(id: number, format: string, selectedVariables: string[]): Observable<any>;

    deleteJsonFile(id: number): Observable<any>;
}
