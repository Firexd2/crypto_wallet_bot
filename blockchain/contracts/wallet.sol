pragma solidity ^0.8.7;

contract Wallet {
    mapping (string => string) public _private_to_external_keys;
    mapping (string => uint) public _balances;

    event Deposit(string _external_key, uint _buyer_id);

    function registerWallet(string memory _external_key, string memory _private_key) public {
        _private_to_external_keys[_private_key] = _external_key;
        _balances[_external_key] = 0;
    }

    function getBalance(string memory _external_key) public view returns(uint) {
        return _balances[_external_key];
    }

    function deposit(string memory _external_key, uint _buyer_id) public payable {
        _balances[_external_key] += msg.value;

        emit Deposit(_external_key, _buyer_id);
    }

    function withdrawal(string memory _private_key, uint _value, address payable _to) public {
        string memory _external_key = _private_to_external_keys[_private_key];
        require(_value <= _balances[_external_key]);
        _balances[_external_key] -= _value;
        _to.transfer(_value);
    }
}
