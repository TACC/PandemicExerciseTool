IP ?= ERROR

ping:
	ansible --key-file ~/.ssh/jetstream -u ubuntu --module-name ping -i inventory.ini dev

play:
	ansible-playbook --key-file ~/.ssh/jetstream -u ubuntu -i inventory.ini playbook.yaml

kill:
	ansible-playbook --key-file ~/.ssh/jetstream -u ubuntu -i inventory.ini kill.yaml

prune:
	ansible-playbook --key-file ~/.ssh/jetstream -u ubuntu -i inventory.ini prune.yaml

fix:
	ansible-playbook --key-file ~/.ssh/jetstream -u ubuntu -i inventory.ini -l $(IP) -t dash playbook.yaml
