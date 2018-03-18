#include <stdio.h>
#include <zmq/zmq.h>

int main()
{
	void *context = zmq_init(1);
	if (!context)
	{
		fprintf(stderr, "Error: Couldn't initialize ZeroMQ.\n");
		return -1;
	}

	int major, minor, patch;
	zmq_version(&major, &minor, &patch);
	printf("Successfully initialized ZeroMQ %d.%d.%d\n", major, minor, patch);

	zmq_term(context);
	return 0;
}
