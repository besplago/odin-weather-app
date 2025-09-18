export class View {
  constructor() {}

  // --- Weather ---
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

  setIcon(iconUrl) {
    const icon = document.getElementById("icon");
    icon.src = iconUrl;
  }

  setTheme(theme) {
    document.body.className = theme;
  }

  bindLocationChanged(handler) {
    const cityInput = document.getElementById("city")
    cityInput.addEventListener("change", event => {
      const newLocation = event.target.value
      handler(newLocation)
    })
  }

  // --- Player ---
  setLastName(lastNameString) {
    const lastName = document.getElementById("lastName");
    lastName.innerHTML = lastNameString;
  }

  setFirstName(firstNameString) {
    const firstName = document.getElementById("firstName");
    firstName.innerHTML = firstNameString;
  }

  setPlayerCountry(countryString) {
    const country = document.getElementById("playerCountry");
    country.innerHTML = countryString;
  }

  setHeight(heightString) {
    const height = document.getElementById("height");
    height.innerHTML = heightString;
  }

  setPosition(positionString) {
    const position = document.getElementById("position");
    position.innerHTML = positionString;
  }

  setTeam(teamString) {
    const team = document.getElementById("team");
    team.innerHTML = teamString;
  }

  setVideo(videoId) {
    const video = document.getElementById("video");
    video.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
  }
}
