export class Presenter {
  constructor(time, weather, view) {
    this.time = time;
    this.weather = weather;
    this.view = view;

    this.fetchWeatherData("Copenhagen")
      .then((data) => this.weather.setData(data))
      .then(() => {
        this.view.setTemperature(
          this.roundTemperature(this.weather.temperature)
        );
        this.view.setCity(this.weather.city);
        this.view.setCountry(this.weather.country);
        this.view.setCondition(this.weather.condition.text);
        this.view.setWindSpeed(this.weather.windSpeed);
      });
    setInterval(this.updateTime, 1000);
  }

  roundTemperature(temperatureString) {
    return Number(Math.round(temperatureString)).toString();
  }

  updateTime = () => {
    this.view.setTime(this.time.getTime());
  };

  async fetchWeatherData(location) {
    const key = "852f08d906934fd18d9191846251109";
    const response = await fetch(
      `https://api.weatherapi.com/v1/current.json?key=${key}&q=${location}&aqi=no`
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
