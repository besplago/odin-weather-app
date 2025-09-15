export class Weather {
  constructor() {
    this.temperature = null;
    this.city = null;
    this.country = null;
    this.condition = null;
    this.windSpeed = null;

    this.loaded = false;
  }

  setData({ temperature, city, country, condition, windSpeed }) {
    this.temperature = temperature;
    this.city = city;
    this.country = country;
    this.condition = condition;
    this.windSpeed = windSpeed;
    this.loaded = true;
  }
}
