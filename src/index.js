import "./styles.css";
import "./template.html";
import { Presenter } from "./js/presenter";
import { View } from "./js/view";
import { Time } from "./js/timeModel";
import { Weather } from "./js/weatherModel";
import { Player } from "./js/playerModel";

document.addEventListener("DOMContentLoaded", () => {
  const timeModel = new Time();
  const weatherModel = new Weather();
  const playerModel = new Player();
  const view = new View();
  const presenter = new Presenter(timeModel, weatherModel, playerModel, view);
});
