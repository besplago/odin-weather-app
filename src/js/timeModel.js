export class Time {
  constructor() {
    this.currentTime = null;
  }

  tick() {
    this.currentTime.setSeconds(this.currentTime.getSeconds() + 1);
  }

  getTime() {
    return this.currentTime.toLocaleTimeString();
  }

  setStartTime(startTimeString) {
    this.currentTime = new Date(startTimeString);
  }
}
