var YourContractName = artifacts.require("Counter");

module.exports = function(deployer) {
    deployer.deploy(YourContractName);
};