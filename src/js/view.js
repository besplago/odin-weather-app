export class View {
  constructor() {}

  setTime(timeString) {
    const time = document.getElementById("time");
    time.innerHTML = timeString;
    console.log(timeString);
  }
}
