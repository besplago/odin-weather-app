export class Weather {
  constructor() {
    this.temperature = null;
    this.city = null;
    this.country = null;
    this.condition = null;
    this.windSpeed = null;
    this.theme = null;

    this.loaded = false;
  }

  setData({
    temperature,
    city,
    country,
    condition,
    windSpeed,
    isDay,
    icon,
    theme,
  }) {
    this.temperature = temperature;
    this.city = city;
    this.country = country;
    this.condition = condition;
    this.windSpeed = windSpeed;
    this.isDay = isDay;
    this.icon = icon;
    this.theme = theme;

    this.loaded = true;
  }
}
