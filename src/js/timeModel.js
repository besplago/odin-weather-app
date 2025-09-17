export class Time {
  constructor() {
    this.currentTime = null;
  }

  tick() {
    if (this.currentTime) {
      this.currentTime.setSeconds(this.currentTime.getSeconds() + 1);
    }
  }

  getTime() {
    if (!this.currentTime) return "";
    return this.currentTime.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  }

  setStartTime(startTimeString) {
    this.currentTime = new Date(startTimeString);
  }
}
