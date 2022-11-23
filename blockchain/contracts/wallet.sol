pragma solidity ^0.8.7;

contract Wallet {
    mapping (uint => uint) private _private_keys;
    mapping (uint => uint) private _balances;

    event Deposit(uint _external_key, uint _buyer_id);

    function random() private view returns (uint) {
        return uint(keccak256(block.difficulty, now));
    }

    function registerWallet() public returns(uint, uint) {
        uint _external_key = random();
        uint _private_key = random();

        _private_keys[_external_key] = _private_key;
        _balances[_external_key] = 0;

        return (_external_key, _private_key);
    }

    function getBalance(uint _external_key) public view returns(uint) {
        return _balances[_external_key];
    }
    function deposit(uint _external_key, uint _buyer_id) public payable {
        _balances[_external_key] += msg.value;
        emit Deposit(_external_key, _buyer_id);
    }
    function withdrawal(uint _private_key, uint _value, address _to) public {
        uint _external_key = _private_keys[_private_key];
        require(_value <= _balances[_external_key]);
        _balances[_external_key] -= _value;
        _to.transfer(_value);
    }
}
