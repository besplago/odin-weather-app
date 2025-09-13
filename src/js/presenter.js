export class Presenter {
  constructor(time, view) {
    this.time = time;
    this.view = view;
    console.log(this.view);

    setInterval(this.updateTime, 1000);
  }

  updateTime = () => {
    this.view.setTime(this.time.getTime());
  };
}
