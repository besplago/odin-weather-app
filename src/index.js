import "./styles.css";
import "./template.html";
import { Presenter } from "./js/presenter";
import { View } from "./js/view";
import { Time } from "./js/timeModel";

const key = "ELSDJPML3MP99HR775X4UTM2N";

async function fetchWeather() {
  // TODO: Instead of using API, just load players from a local file instead.
  const today = new Date();
  const dd = String(today.getDate()).padStart(2, "0");
  const mm = String(today.getMonth() + 1).padStart(2, "0");
  const yyyy = today.getFullYear();
  const response = await fetch(
    `https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/copenhagen/${yyyy}-${mm}-${dd}/?key=${key}`
  );
  return response.json();
}

document.addEventListener("DOMContentLoaded", () => {
  const timeModel = new Time();
  const view = new View();
  const presenter = new Presenter(timeModel, view);
});
