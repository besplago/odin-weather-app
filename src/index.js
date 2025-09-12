import "./styles.css";
import "./template.html";

async function getPlayers() {
  // TODO: Instead of using API, just load players from a local file instead.
  //   const response = await fetch("https://api.balldontlie.io/v1/players", {
  //     headers: { Authorization: "ab7d3912-b6a7-42f1-acec-11659c260395" },
  //   });
  //   return response.json();
}

document.addEventListener("DOMContentLoaded", () => {
  getPlayers().then((response) => console.log(response));
});
