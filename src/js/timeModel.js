export class Time {
  constructor() {}

  // TODO: Currently is just local time, should be location dependent.
  // Either use a lib or use the time from the weather api and count from there
  getTime() {
    const now = new Date();
    return now.toLocaleTimeString();
  }
}
