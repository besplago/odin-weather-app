export class Presenter {
  constructor(time, weather, view) {
    this.time = time;
    this.weather = weather;
    this.view = view;

    this.fetchWeatherData().then((data) => this.weather.setData(data));
    setInterval(this.updateTime, 1000);
  }

  updateTime = () => {
    this.view.setTime(this.time.getTime());
  };

  async fetchWeatherData() {
    const key = "852f08d906934fd18d9191846251109";
    const response = await fetch(
      `https://api.weatherapi.com/v1/current.json?key=${key}&q=London&aqi=no`
    );
    const jsonData = await response.json();
    return {
      temperature: jsonData.current.temp_c,
      city: jsonData.location.name,
      country: jsonData.location.country,
      condition: jsonData.current.condition,
      windSpeed: jsonData.current.wind_kph,
    };
  }
}
