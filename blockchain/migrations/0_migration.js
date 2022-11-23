var ContractName = artifacts.require("Wallet");

module.exports = function(deployer) {
    deployer.deploy(ContractName);
};