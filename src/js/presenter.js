// import { readFile } from "fs/promises";

export class Presenter {
  constructor(time, weather, player, view) {
    this.time = time;
    this.weather = weather;
    this.player = player;
    this.view = view;

    this.init();

    setInterval(this.updateTime, 1000);
  }

  async init() {
    try {
      const weatherData = await this.fetchWeatherData("Kastrup");
      this.weather.setData(weatherData);
      this.loadWeatherToView();

      const playerData = await this.fetchPlayerData(
        this.roundTemperature(this.weather.temperature)
      );
      this.player.setData(playerData);
      this.loadPlayerToVIew();

      const searchQuery = `${this.player.firstName} ${this.player.lastName} ${this.player.team} highlights`;

      const youtubeVideoId = await this.searchYouTube(searchQuery);
      this.loadVideoToView(youtubeVideoId);
    } catch (error) {
      alert("Could not find that place.");
      console.error(error);
    }
  }

  async searchYouTube(query) {
    const apiKey = "AIzaSyCAqQAYaKefV3ncjbeu4RVYoUDqzMpC9Zc";
    const maxResults = 5;
    const url = `https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=${maxResults}&q=${encodeURIComponent(
      query
    )}&key=${apiKey}`;

    const response = await fetch(url);
    const data = await response.json();

    if (data.items && data.items.length > 0) {
      const randomIndex = Math.floor(Math.random() * data.items.length);
      return data.items[randomIndex].id.videoId;
    } else {
      return null;
    }
  }

  loadWeatherToView() {
    this.view.setTemperature(this.roundTemperature(this.weather.temperature));
    this.view.setCity(this.weather.city);
    this.view.setCountry(this.weather.country);
    this.view.setCondition(this.weather.condition.text);
    this.view.setWindSpeed(this.weather.windSpeed);
    this.view.setIcon(this.weather.icon);
  }

  loadPlayerToVIew() {
    this.view.setLastName(this.player.lastName);
    this.view.setFirstName(this.player.firstName);
    this.view.setPlayerCountry(this.player.country);
    this.view.setHeight(this.player.height);
    this.view.setPosition(this.player.position);
    this.view.setTeam(this.player.team);
  }

  loadVideoToView(videoUrl) {
    this.view.setVideo(videoUrl);
  }

  roundTemperature(temperatureString) {
    return Number(Math.round(temperatureString)).toString();
  }

  updateTime = () => {
    this.view.setTime(this.time.getTime());
  };

  async fetchPlayerData(jerseyNumber) {
    const playerProfiles = require("../assets/players_profiles.json");
    let playersWithJerseyNumber = [];
    playerProfiles.forEach((playerProfile) => {
      if (playerProfile.jersey_number == jerseyNumber) {
        playersWithJerseyNumber.push(playerProfile);
      }
    });
    const selectedPlayer =
      playersWithJerseyNumber[
        Math.floor(Math.random() * playersWithJerseyNumber.length)
      ];

    return {
      lastName: selectedPlayer.last_name,
      firstName: selectedPlayer.first_name,
      country: selectedPlayer.country,
      height: selectedPlayer.height,
      position: selectedPlayer.position,
      team: selectedPlayer.team.name,
    };
  }

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
      isDay: jsonData.current.is_day,
      icon: jsonData.current.condition.icon,
    };
  }
}
