export class Presenter {
  constructor(view) {
    this.view = view;
    console.log(this.view);

    setInterval(this.updateTime, 1000);
  }

  // TODO: Currently is just local time, should be location dependent.
  // Either use a lib or use the time from the weather api and count from there
  // Also, this should be its own model, and not in the presenter
  updateTime = () => {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    this.view.setTime(timeString);
  };
}
