import os
from functools import wraps

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.instrumentation.pymysql import PyMySQLInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# リソースを設定
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: os.environ.get("SERVICE_NAME_IDENTIFIER") + "_" + os.environ.get("SERVICE_NAME"),
})

trace.set_tracer_provider(
    TracerProvider(
        resource=resource,
        active_span_processor=BatchSpanProcessor(
            OTLPSpanExporter(endpoint=os.environ.get("TRACE_PROVIDER_ENDPOINT"))
        ),
    )
)
tracer = trace.get_tracer(__name__)

# tracer = trace.get_tracer_provider().get_tracer(__name__)

def tracing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # デコレータを付与する関数名・メソッド名の qualified name
        name = func.__qualname__

        # デコレータが付与された関数名を span の名前として指定する
        with tracer.start_as_current_span(name=name):

            # sql と requests の自動計装
            PyMySQLInstrumentor().instrument(enable_commenter=True, commenter_options={})
            RequestsInstrumentor().instrument()

            return func(*args, **kwargs)

    return wrapper

# 指定したデコレータをClass内の全メソッドに付与する
def put_decorator_on_all_methods(decorator, cls=None):
    if cls is None:
        return lambda cls: put_decorator_on_all_methods(decorator, cls)

    class Decoratable(cls):
        def __init__(self, *args, **kargs):
            super().__init__(*args, **kargs)

        def __getattribute__(self, item):
            value = object.__getattribute__(self, item)
            if callable(value):
                return decorator(value)
            return value

    return Decoratable