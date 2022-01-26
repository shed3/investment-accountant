<div id="top"></div>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![MIT License][license-shield]][license-url]
![top-languages-shield]
![languages-count-shield]
![status-shield]
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <!-- <a href="https://github.com/shed3/investment-accountant">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a> -->
  <h2 align="center">Investment Accountant</h2>
  <p align="center">
    <i>Create financial statements from real world investment transactions</i>
    <br />
    <br />
    <a href="https://github.com/shed3/investment-accountant/issues">Report Bug</a>
    ·
    <a href="https://github.com/shed3/investment-accountant/issues?q=is%3Aopen+is%3Aissue+label%3Aenhancement">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About the Investment Accountant</a></li>
    <li>
        <a href="#object-reference">Object Reference</a>
        <ul><a href="#asset">Asset</a></ul>
        <ul><a href="#entry">Entry</a></ul>
        <ul><a href="#transaction">Transaction</a></ul>
        <ul><a href="#ledger">Ledger</a></ul>
        <ul><a href="#bookkeeper">Bookkeeper</a></ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>
<br />

<!-- ABOUT THE PROJECT -->
## About Investment Accountant

Investment Accountant provides a simple interface for creating financial statements from real world financial investment transactions. The Investment Accountant uses double entry accounting principles and strives to be GAAP compliant. There are some default transaction classes available for use and extension. Transactions can represent buying/selling a stock, sending/receiving a cryptocurrency, or anything else you can think of!

## Object Reference

### Asset
An Asset represents the financial asset involved in a transaction. It contains useful information such as its symbol and whether it is stable or fiat. The Asset component is used to unify the interface and provide the data that is used throughout the system (for example, in the Positions and Entries).

### Entry
An Entry is the basic unit of accounting in this system. Each transaction must have at least two corresponding entries to keep the equation equal, however a single transaction may have many correlating entries. 

### Transaction
Transactions must contain all of the information needed in order for the bookkeeper to accurately account for it. Initially, we are accounting for investment transactions so we have to provide the relevant Asset information to track, and provide entry_templates which explain how it is tracked in accounts. In other accounting systems, Asset may be substituted for an inventory, equipment, land, or other physical items that are involved in transactions. This will require new entry templates, and further functions to accurately represent the accounting involved.

### Ledger
The Ledger consumes accounting journal entries and manipulates 
those entries within a pandas dataframe. The Ledger provides a 
simple interface for organizing data into common accounting structures.

### Bookkeeper

The Bookkeeper converts `Transactions` to `Entries` and maintains a `Ledger` and `Positions`. It is responsible for enforcing Transaction, Entry, Position, and Ledger interfaces.

A Bookkeeper can

 * Accept transaction(s), which will trigger 
   1. Update Assets' Position
   2. Get Entries from Transaction
   3. create Adjusting Entries for Affected Positions
   4. Record Transaction and Adjusting Entries on Ledger

 * Accept New Asset Price
    1. Update Assets' Position
    2. Create Adjusting Entries for Asset Positions
    3. Record Adjusting Entries on Ledger

<!-- ROADMAP -->
## Roadmap

- [x] Finalize Transaction interface
- [x] Finalize Entry interface
- [x] Finalize Position interface
- [ ] Create financial statements
- [ ] Allow Bookkeeper to maintain correct books in real-time environment
- [ ] Add usage docs

See the [open issues][github-issues] for a full list of proposed features (and known issues).

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch
   ```sh
   git checkout -b feature/AmazingFeature
   ```
3. Commit your Changes 
    ```sh
    git commit -m 'Add some AmazingFeature'
    ```
4. Push to the Branch 
   ```sh
    git push origin feature/AmazingFeature
    ```
6. Open a Pull Request


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.
**Free Software, Yee Haw!**

<!-- CONTACT -->
## Contact

Riley Stephens - rileystephens@escalatorllc.com

<p align="right"><a href="#top">back to top</a></p>



<!-- Project URLS-->
[github-url]: https://github.com/shed3/investment-accountant
[github-issues]: https://github.com/shed3/investment-accountant/issues
[repo-path]: shed3/investment-accountant

<!-- License Badge -->
[license-shield]: https://img.shields.io/github/license/shed3/investment-accountant.svg?style=for-the-badge
[license-url]: https://github.com/shed3/investment-accountant/blob/main/LICENSE.txt

<!-- Version Badge -->
[package-version-shield]: https://img.shields.io/github/package-json/v/shed3/investment-accountant.svg?style=for-the-badge

<!-- Build Status Badge -->
[build-status-shield]: https://img.shields.io/travis/com/shed3/investment-accountant.svg?style=for-the-badge

<!-- Contributors Badge -->
[contributors-shield]: https://img.shields.io/github/contributors/shed3/investment-accountant.svg?style=for-the-badge
[contributors-url]: https://github.com/shed3/investment-accountant/graphs/contributors

<!-- Languages Badge-->
[top-languages-shield]: https://img.shields.io/github/languages/top/shed3/investment-accountant.svg?style=for-the-badge

[languages-count-shield]: https://img.shields.io/github/languages/count/shed3/investment-accountant.svg?style=for-the-badge

[status-shield]: https://img.shields.io/static/v1?label=status&message=under%20construction&color=red&style=for-the-badge