import { Injectable } from '@angular/core';
import { Router, NavigationStart } from '@angular/router';
import { Observable, Subject } from 'rxjs';
import { IAlertService } from '../interfaces/alert-service';

interface AlertMessage {
  type: 'success' | 'error';
  text: string;
}

@Injectable({
  providedIn: 'root'
})
export class AlertService implements IAlertService {
  private subject = new Subject<AlertMessage | null>();
  private keepAfterNavigationChange = false;

  constructor(private router: Router) {
    router.events.subscribe(event => {
      if (event instanceof NavigationStart) {
        if (this.keepAfterNavigationChange) {
          this.keepAfterNavigationChange = false;
        } else {
          this.subject.next(null);
        }
      }
    });
  }

  success(message: string, keepAfterNavigationChange: boolean = false) {
    this.keepAfterNavigationChange = keepAfterNavigationChange;
    this.subject.next({ type: 'success', text: message });
  }

  error(message: string | Error, keepAfterNavigationChange: boolean = false) {
    this.keepAfterNavigationChange = keepAfterNavigationChange;
    const errorMessage = message instanceof Error ? message.message : message;
    this.subject.next({ type: 'error', text: errorMessage });
  }

  getMessage(): Observable<AlertMessage | null> {
    return this.subject.asObservable();
  }
}
