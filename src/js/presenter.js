export class Presenter {
  constructor(time, weather, view) {
    this.time = time;
    this.weather = weather;
    this.view = view;

    setInterval(this.updateTime, 1000);
  }

  updateTime = () => {
    this.view.setTime(this.time.getTime());
  };
}
