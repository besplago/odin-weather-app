export class Weather {
  constructor() {
    this.temperature = null;
    this.city = null;
    this.country = null;
    this.weatherDescription = null;
    this.windSpeed = null;

    this.loaded = false;
  }

  setData(temperature, city, country, weatherDescription, windSpeed) {
    this.temperature = temperature;
    this.city = city;
    this.country = country;
    this.weatherDescription = weatherDescription;
    this.windSpeed = windSpeed;
    this.loaded = true;
  }
}
