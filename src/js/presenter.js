export class Presenter {
  constructor(view) {
    this.view = view;
    console.log(this.view);

    setInterval(this.updateTime, 1000);
  }

  updateTime = () => {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    this.view.setTime(timeString);
  };
}
