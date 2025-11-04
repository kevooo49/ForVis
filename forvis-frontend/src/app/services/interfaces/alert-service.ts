import {Observable} from 'rxjs';
import {InjectionToken} from '@angular/core';

export const ALERT_SERVICE = new InjectionToken<IAlertService>('AlertService');

export interface IAlertService {
  success(message: string, keepAfterNavigationChange: boolean): void;

  error(message: any, keepAfterNavigationChange?: boolean): void;

  getMessage(): Observable<any>;
}
