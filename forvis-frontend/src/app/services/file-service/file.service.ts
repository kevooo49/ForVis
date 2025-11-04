import {Inject, Injectable} from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {AUTH_SERVICE, IAuthService} from "../interfaces/auth-service";
import {IFileService} from "../interfaces/file-service";

@Injectable({
  providedIn: 'root'
})
export class FileService implements IFileService {

  url_sat_files = '/api/profile/files/sat/';
  url_sat_file = '/api/profile/file/sat/';
  url_maxsat_files = '/api/profile/files/max-sat/';
  url_maxsat_file = '/api/profile/file/max-sat/';
  url_vis_2clause_files = '/api/profile/files/vis_2clause/';
  url_vis_2clause_file = '/api/profile/file/vis_2clause/';

  constructor(
      private http: HttpClient,
      @Inject(AUTH_SERVICE) private authService: IAuthService
  ) {}

  getSatFilesList(): Observable<any> {
    return this.http.get(this.url_sat_files, this.authService.authOptions());
  }

  getSatFile(id: number, format: string, selectedVariables: string[] = []): Observable<any> {
    let params = new HttpParams();

    if (selectedVariables.length > 0) {
      params = params.set('selectedVariables', selectedVariables.join(','));
    }

    return this.http.get(`${this.url_sat_file}${id}/${format}/`, {
      ...this.authService.authOptions(),
      params: params
    });
  }

  deleteSatFile(id: number): Observable<any> {
    return this.http.delete(`${this.url_sat_file}${id}/del/`, this.authService.authOptions());
  }

  getMaxSatFilesList(): Observable<any> {
    return this.http.get(this.url_maxsat_files, this.authService.authOptions());
  }

  getMaxSatFile(id: number, format: string, selectedVariables: string[] = []): Observable<any> {
    let params = new HttpParams();

    if (selectedVariables.length > 0) {
      params = params.set('selectedVariables', selectedVariables.join(','));
    }

    return this.http.get(`${this.url_maxsat_file}${id}/${format}/`, {
      ...this.authService.authOptions(),
      params: params
    });
  }

  deleteMaxSatFile(id: number): Observable<any> {
    return this.http.delete(`${this.url_maxsat_file}${id}/del/`, this.authService.authOptions());
  }

  getVis2ClauseFilesList(): Observable<any> {
    return this.http.get(this.url_vis_2clause_files, this.authService.authOptions());
  }

  getVis2ClauseFile(id: number, format: string): Observable<any> {
    return this.http.get(`${this.url_vis_2clause_file}${id}/${format}/`, this.authService.authOptions());
  }

  deleteVis2ClauseFile(id: number): Observable<any> {
    return this.http.delete(`${this.url_vis_2clause_file}${id}/del/`, this.authService.authOptions());
  }
}
