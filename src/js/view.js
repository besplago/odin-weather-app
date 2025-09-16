export class View {
  constructor() {}

  setTemperature(temperatureString) {
    const temperature = document.getElementById("temperature");
    temperature.innerHTML = temperatureString;
  }

  setTime(timeString) {
    const time = document.getElementById("time");
    time.innerHTML = timeString;
  }

  setCity(cityString) {
    const city = document.getElementById("city");
    city.innerHTML = cityString;
  }

  setCountry(countryString) {
    const country = document.getElementById("country");
    country.innerHTML = countryString;
  }

  setCondition(conditionString) {
    const conditionEl = document.getElementById("condition");
    conditionEl.innerHTML = conditionString;
  }

  setWindSpeed(windSpeedString) {
    const wind = document.getElementById("wind");
    wind.innerHTML = `${windSpeedString} km/h`;
  }
}
