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
    // TODO: Bruh, implement this with weather API, not visual crossing
    const key = "ELSDJPML3MP99HR775X4UTM2N";
    const today = new Date();
    const dd = String(today.getDate()).padStart(2, "0");
    const mm = String(today.getMonth() + 1).padStart(2, "0");
    const yyyy = today.getFullYear();
    const response = await fetch(
      `https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/copenhagen/${yyyy}-${mm}-${dd}/?key=${key}`
    );
    return response.json();
  }
}
