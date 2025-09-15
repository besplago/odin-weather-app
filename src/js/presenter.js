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

  async fetchWeatherResponse() {
    const key = "852f08d906934fd18d9191846251109";
    const response = await fetch(
      `https://api.weatherapi.com/v1/current.json?key=${key}&q=London&aqi=no`
    );
    return response.json();
  }
}
