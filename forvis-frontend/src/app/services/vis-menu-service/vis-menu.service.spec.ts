import { TestBed } from '@angular/core/testing';

import { VisMenuService } from './vis-menu.service';

describe('AuthService', () => {
  let service: VisMenuService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(VisMenuService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
