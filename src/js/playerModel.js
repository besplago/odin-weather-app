export class Player {
  constructor() {
    this.lastName = null;
    this.firstName = null;
    this.country = null;
    this.height = null;
    this.position = null;
    this.team = null;
  }

  setData({ lastName, firstName, country, height, position, team }) {
    this.lastName = lastName;
    this.firstName = firstName;
    this.country = country;
    this.height = height;
    this.position = position;
    this.team = team;
  }
}
