export class Weather {
  constructor() {
    this.fetchWeatherResponse().then((weatherData) =>
      this.initWeather(weatherData)
    );
  }

  initWeather(weatherData) {
    console.log(weatherData);
  }

  async fetchWeatherResponse() {
    const key = "852f08d906934fd18d9191846251109";
    const response = await fetch(
      `https://api.weatherapi.com/v1/current.json?key=${key}&q=London&aqi=no`
    );
    return response.json();
  }
}
