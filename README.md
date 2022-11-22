# whatsappShare

**基于WhatsApp iOS协议逆向的共享资源**

**<font color="#01847"> WhatsApp api 全量协议（可实现注册登录，发消息，群组头像功能，有需要技术支持及源码可联系 telegram：@tgforme2） </font>**

****
## 0x01. WhatsApp ipa 脱壳 历史版本


- 最近版本: [whatsapp_2.21.110.zip](/versions/)



****
## 0x02. WhatsApp iOS协议部分
![](/login.png)


# **0x01 工具**

首先是要用到的工具，中间主要用了ida，hopper和lldb

- dumpdecrypted: 将苹果加密过的app砸壳
- class-dump: 导出MachO文件里ObjC类及方法定义
- CydiaSubstrate: 将第三方动态库注入进程
- Cycript: 用js语法写ObjC方法
- Theos: 越狱插件开发工具
- IDA: 反汇编、反编译工具
- Hopper: OSX反汇编、反编译工具
- Debugserver + LLDB: 动态调试器

# **0x02 ARM指令**

```
arm是RISC结构，数据从内存到CPU之间移动只能通过L/S指令来完成，就是ldr/str指令
ldr 把数据从内存移到cpu
str 把cpu的数据数据转移到内存
lldb读取内存的数据，memory read <start> <end>
ldr r0, 0x12345678   //把0x12345678这个地址中的值存放到r0中
ldr r0, =0x12345678  //把0x12345678这个地址写到r0中
例子：
COUNT EQU 0x40003100 //定义一个COUNT变量，地址是0x40003100
...
LDR R1,=COUNT       //将COUNT这个变量的地址，也就是0x40003100放到R1中
MOV R0,#0           //将立即数0放到R0中
STR R0,[R1]         //将R0中的值放到以R1中的值为地址的存储单元去

B 跳转指令
BL 带返回的跳转指令
BLX 带返回和状态切换的跳转指令
BX  带状态切换的跳转指令

BLX指令从ARM指令集跳转到指令中所指定的目标地址，并将处理器的工作状态从ARM切换到Thumb状态，该指令同时将PC的当前内容保存到寄存器R14，因此，当子程序使用Thumb指令集，而调用者者使用ARM指令集，可以通过BLX指令实现子程序的调用和处理器工作状态切换，同时，子程序的返回可以通过将寄存器R14的值复制到PC中来完成。
　R0-R3:　　　　　　　　用于函数参数及返回值的传递，超过4个参数，其它参数存在栈中，在ARM中栈是向下生长的，R0还可以作为返回值。
　　R4-R6, R8, R10-R11:　没有特殊规定，就是普通的通用寄存器
　　R7:　　　　　　　　　　栈帧指针，指向母函数与被调用子函数在栈中的交界。
　　R9:　　　　　　　　　　在iOS3.0被操作系统保留
　　R12:　　　　　　　　　 内部过程调用寄存器，动态链接时会用到，不必深究
　　R13:　　　　　　　　　 SP(stack pointer)，是栈顶指针
　　R14:　　　　　　　　　 LR(link register)，存放函数的返回地址。
　　R15:　　　　　　　　　 PC(program counter)，指向当前指令地址。
ADC 　　 带进位的加法
　　ADD 　　 加法
　　AND 　　 逻辑与
　　B 　　　  分支跳转，很少单独使用
　　BL          分支跳转，跳转后返回地址存入r14
　　BX          分支跳转，并切换指令模式（Thumb/ARM）
　　CMP        比较值，结果存在程序状态寄存器，一般用于分支判断
　　BEQ        结果为0则跳转
　　BNE        结果不为0跳转
　　LDR        加载寄存器，从内存加载到寄存器
　　LDRB      装载字节到寄存器
　　LDRH      装载半字到寄存器（一个字是32位）
　　LSL         逻辑左移 这是一个选项，不是指令
　　LSR         逻辑右移 这是一个选项，不是指令
　　MOV        传送值/寄存器到一个寄存器
　　STR         存储一个寄存器，寄存器值存到内存
　　STRB       存储一个字节
　　STRH       存储一个半字
　　SUB         减法
　　PUSH POP 堆栈操作

有时候需要

db  ；定义字节类型变量，一个字节数据占一个字节单元，读完一个偏移量加1
dw  ；定义字类型变量，一个字数据占2个字节单元，读完一个，偏移量加2
dd  ；定义双字类型变量，一个双字数据占4个字节单元，读完一个，偏移量加4

IDA给某个位置命名的时，它会使用该位置的虚拟地址和表示一个该地址的类型的前缀进行命名：
sub_xxx  ；地址xxx处的子例程
loc_xxx  ；地址xxx处的一个指令
byte_xxx ；位置xxx处的8位数据
word_xxx ;位置xxx处的16位数据
dword_xxx ;位置xxx处的32位数据
unk_xxx   ;位置xxx处大小未知的数据
```

```
关于sp，bp等栈寄存器的解释：
SP is stack pointer. The stack is generally used to hold "automatic" variables and context/parameters across function calls. Conceptually you can think of the "stack" as a place where you "pile" your data. You keep "stacking" one piece of data over the other and the stack pointer tells you how "high" your "stack" of data is. You can remove data from the "top" of the "stack" and make it shorter.

<https://www.zybuluo.com/oro-oro/note/137244>
<http://cryptroix.com/2016/10/16/journey-to-the-stack/>
<http://en.citizendium.org/wiki/Stack_frame>
虽然是英文，但是看起来要比中文易懂
```

ida里面有三种颜色的箭头:

1. 蓝色，顺序执行
2. 绿色，条件为(YES)
3. 红色，条件为（NO）

# **0x03 lldb使用方法**

```
lldb操作相关指令
image list -o -f 查看进程在虚拟内存中相对模块基地址
br s -a [addr]  打断点
breakpoint delete <breakpoint> 删除断点
s/n  是针对源代码
br list 列出所有断点
br dis 1  禁用序号为1的断点
jump <address> 跳转到新地址

ni   断点的单步之行, netxi(next instruction简写:ni)
si   stepi(step instruction 简写:si)
display /10i $pc-16  显示当前PC附近的10条指令

si会进入函数之行，ni执行完但是不会进入函数内，执行过程中可以利用display /i $pc来看下一个执行的instruction是什么

c  放开执行该断点
p  输出某个寄存器的值
p $r0  输出寄存器的内容
也可以将一个地址所存放的值进行打印
p/x $sp 就是输出$sp指针所指的地址处存放的值，以16进制表示
po (char *)$r2   po打印Object-C对象
register read --all  读取所有的寄存器内容
thread list ／／打印所有线程
thread select  ／／跳到某个线程
thread info ／／输出当前线程信息
frame variable  ／／打印当前栈所有变量
frame variable '变量名' ／／打印某个变量
frame info 查看当前帧栈信息
frame select 跳到指定帧栈

```

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/fab55b3e-f5fc-47fc-852e-3b594f06239d/Untitled.png)

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/bf7ab224-5abd-47de-aece-a5affc5e2887/Untitled.png)

frida的常见用法：

- hook函数(IOS中theos具备的功能）
- 记录函数执行日至(IOS中theos具备的功能）
- 调用函数（IOS中cycript具备的功能）
- 读写内存（类似调试器的功能）

lldb:

- lldb在object-c类对象所有函数设置断点: `breakpoint set -r '\[ClassName .*\]$'`

常用：

```
breakpoint set --name <method-name>
    "set a breakpoint on a given function name, globally. eg.
     breakpoint set --name viewDidLoad
     or
     breakpoint set --name "-[UIView setFrame:]"

break set --selector <selector-name>
    "set a breakpoint on a selector, globally. e.g.,
    breakpoint set --selector dealloc
bt  //查看堆栈
frame select <framenum>
thread list
expression $r6 //查看r6寄存器的值
1. 加参数可以更改显示方式，如/x十六进制打印
2. po一般用作查看对象信息
3. po的命令是“expression -O -"命令的别名

第一次使用malloc_info需要在lld里面导入lldb.macosx.heap
malloc_info -s <address>
memory read <start_address> <end_address> 读取内存的值
```

### **0x04 Hopper基本使用**

hopper和LLDB所选择的ARM架构位数得一致，要么是32位，要么都是64位，计算公式：hopper里面显示的都是"模块偏移前基地址",而lldb要操作的都是"模块偏移后的基地址"，所以从hopper到lldb要做一个地址偏移量的转换。

```
偏移后模块基地址 ＝  偏移前模块地址 + ALSR
```

偏移前地址从Hopper看:

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/45ced21a-8ae8-4ed8-a6df-cd7aae57a123/Untitled.png)

ALSR偏移地址从LLDB看:

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/3a3d8caf-af54-462f-ba93-d620d162ec01/Untitled.png)

由上图可知ASLR偏移：30000偏移后基地址为：34000

(从hopper的login搜索找到方法［WCAccountPhoneLoginControlLogic initWithData:]：查看偏移基地址：

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/54be932d-6deb-4fec-b076-8494548ae0a9/Untitled.png)

则偏移后的地址： 14B6A66 + 30000 = 14E6A66设置断点动态调试，使用：

```
br s -a 0x 14E6A66
```

### **0x05 Cycript**

安装Cycript

```
dpkg -i cycript_0.9.461_iphoneos-arm.deb
dpkg -i libffi_1-3.0.10-5_iphoneos-arm.deb

cycript -p <pid>
```

步骤：

安装cydia之后的ssh，然后mac本机：

```
brew install usbmuxd
iproxy 2222 22   //iphone的22端口转发到本机的2222
ssh root@localhost -p 2222  //默认密码 alpine
```

```
cycript:
[UIApp description]
[[UIApp keyWindow] recursiveDescription].toString() //输出如下
<UIView: 0x18b1bd60; frame = (10 0; 20 50); layer = <CALayer: 0x18b1be20>>
   |    |    |    |    |    |    |    |    | <UIImageView: 0x18b1bf90; frame = (30 13.5; 10 10); opaque = NO; userInteractionEnabled = NO; layer = <CALayer: 0x18b1b5f0>>
   |    |    |    |    |    |    |    |    | <UITableViewLabel: 0x18b1c070; frame = (44 10; 218 17); text = 'UIView'; userInteractionEnabled = NO; layer = <_UILabelLayer: 0x18b1c190>>

//查看某个UI：
[#0x18b1c070 _ivarDescription].toString()
[#0x15baf520 nextResponder] 某个地址的调用方法

[[UIApp keyWindow] _autolayoutTrace].toString()
//choose传递一个类，可以在内存中找出属于这个类的对象
／／输出对象的属性：
方法1： 简单基本获取方法。
*controller（直接在对象前面加个*）

方法2：方法一无法获取，就使用方法2
[i for (i in *UIApp)]

方法3：建议方法三，方法三能获取到更多
function tryPrintIvars(a){ var x={}; for(i in *a){ try{ x[i] = (*a)[i]; } catch(e){} } return x; }

function printMethods(className, isa) {
  var count = new new Type("I");
  var classObj = (isa != undefined) ? objc_getClass(className)->isa : objc_getClass(className);
  var methods = class_copyMethodList(classObj, count);
  var methodsArray = [];
  for(var i = 0; i < *count; i++) {
    var method = methods[i];
    methodsArray.push({selector:method_getName(method), implementation:method_getImplementation(method)});
  }
  free(methods);
  return methodsArray;
}
```

```
cycript -p Springboard 或 cycript -p pid

#在内存中找一个MD5Signater类的实例对象
choose(MD5Signater)

#调用0x166b4fb0处的对象的show函数
［#0x166b4fb0 show]

#对show函数传入参数3344
[#0x166b4fb0 show:3344]

#新建一个MD5Signater类的实例，并调用它的setSecret函数，传入参数1
obj = [MD5Signater alloc]
[#0x146f1a30 setSecret:1]

在Objective-C中，［someObject somemethod]的底层实现，实际上是objc_msgSend（someObject,someMethod）,其中前一个是Objective-C对象，后者则可以强制转换成一个字符串。
```

在Objective-C里面，成员方法与类方法的区别：

- 成员方法是以减号 "-" 开头 //成员方法必须使用对象调用
- 类方法是以加号开头 "+" //类方法可以直接使用类名调用

### **Objective-C方法名的问题**

```
- (double)pi;

 方法名就是pi

- (int)square:(int)num;

 带参数的方法名有点特殊，冒号后面一定是参数，可以理解为，有几个冒号就有几个参数，把空格后面到参数前面的内容拼起来就是方法名。所以这个方法名是square:（注意冒号）

－ (int)addNum1:(int)num1 addNum2:(int)num2;

 根据上面的方法，这个方法名是addNum1:addNum2:
```

所以根据上面方法名的问题，在cycript里面调用的时候，是这样：

```
cy# choose(PARSEPedometerInfo)
 [#"PARSPedometerInfo<0x12f22cd60>: \n integration=1541 \n iPhone=1541 \n watch=0 \n heartRat=0\n at:2017-12-26 16:00:00 +0000",#"PARSPedometerInfo<0x12f406c90>: \n integration=1541 \n iPhone=1541 \n watch=0 \n heartRat=0\n at:2017-12-26 16:00:00 +0000"]
    也即找到两个PARSPedometerInfo类的对象,随便用其中一个即可
[#0x12f22cd60 setIntegratedSteps:66666]

 setIntegratedSteps是减号开头的函数，如果是+号开头的函数用法则[className funcName:6666]，如下面的函数是+号开头的函数，可以直接调用这个类中的函数，而不用创建这个类的实例：
cy# [PARSCryptDataUtils encryptWithServerTimestamp:"18013790233"]

带减号的函数，要实例化之后才可以调用
带加号的函数，可以直接调用
```

这一部分主要参考[http://3xp10it.cc/%E4%BA%8C%E8%BF%9B%E5%88%B6/2017/12/25/ida%E9%80%9A%E8%BF%87usb%E8%B0%83%E8%AF%95ios%E4%B8%8B%E7%9A%84app/](http://3xp10it.cc/%E4%BA%8C%E8%BF%9B%E5%88%B6/2017/12/25/ida%E9%80%9A%E8%BF%87usb%E8%B0%83%E8%AF%95ios%E4%B8%8B%E7%9A%84app/)文章

### **0x06 调试流程**

如果要使用lldb调试越狱设备上的进程，需要先将connect的端口映射到本地，以1234端口为例：

```
iproxy 1234 1234
然后打开lldb，输入以下命令：
process connect connect://localhost:1234
连接越狱设备，输入：
debugserver *:1234 -a <pid>
只要越狱设备上的debugserver（重签名过的）正常运行，就可以通过lldb进行远程调试
```

越狱设备第一次连接xcode的时候会在/Developer/usr/bin目录下生成一个debugserver，这个debugserver在ios里面运行会失败需要使用ldid签名，需要两个东西：

- ldid [http://7xibfi.com1.z0.glb.clouddn.com/uploads/default/668/c134605bb19a433f.xml](http://7xibfi.com1.z0.glb.clouddn.com/uploads/default/668/c134605bb19a433f.xml)
- xml（文件） [http://joedj.net/ldid](http://joedj.net/ldid)
    
    xml文件保存为`ent.xml`，然后签名：
    
    ```
    ldid -Sent.xml debugserver
    ```
    
    然后回传到ios上面即可，使用wget或者scp（scp失败，这里是用的是wget）
    
    ```
    debugserver 0.0.0.0:1234 "SpringBoard"
    (lldb)process connect connect://<ios>:<port>
    ```
    

### **Object-C 的一些基础知识**

在Objective-C中的“方法调用”其实应该叫做消息传递。以objc_msgSend函数为例子，

```
[person sayHello]
可以解释为调用person对象的sayHello方法，但是如果从Object-C的Runtime角度来说，这个代码世纪是在发送一个消息，这个代码，编译器时机会将它转换成这样一个函数调用：
objc_msgSend(person,@selector(sayHello))
```

第一个参数是要发送消息的实例，也就是person对象。objc_msgSend会先查询它的methodList方法列表，使用第二个参数sayHello

```
苹果文档这样写的
id objc_msgSend(id self, SEL _cmd, ...)
```

将一个消息发送给一个对象，并且返回一个值。其中，self是消息的接受者，_cmd是selector，... 是可变参数列表。

在现代操作系统中，一个线程会被分配一个stack，当一个函数被调用，一个stack frame（帧栈)就会被压到stack里，里面包含这个函数设计的参数，局部变量，返回地址等相关信息。当函数返回这个帧栈之后，这个帧栈就会被销毁。

```
_text:0001D76A MOV R0, #(selRefHTTPMethod - 0x1C776) ; selRef_HTTPMethod
_text:0001D772 ADD R0, PC ; selRefHTTPMethod
__text:0001D774 LDR R1, [R0] ; "HTTPMethod"
__text:0001D776 MOV R0, R10
_text:0001D778 STR R1, [SP,#0xAC+varA0]
_text:0001D77A BLX _objcmsgSend
__text:0001D77E MOV R7, R7
_text:0001D780 BLX _objcretainAutoreleasedReturnValue
__text:0001D784 MOV R4, R0
_text:0001D786 MOV R0, #(selRefsetRequestMethod_ - 0x1C794) ; selRef_setRequestMethod_
__text:0001D78E MOV R2, R4
```

0001D77A处的selector为HTTPMethod，在functions windows里可以搜到这个函数，函数在执行前把调用的对象存储在R0中。

```
__text:0001D774 LDR R1, [R0] ; "HTTPMethod"   ／／把方法名放到R1中
__text:0001D776 MOV R0, R10                    //R0赋值为R10所在的值，此处R10位HTTPMethod这个方法归属的类的指针之类。
上面两条指令确定了调用的函数，调用完方法，如果一个方法有返回值，会更新在R0，大于一个返回值，就会通过栈来返回值。（意思是如果函数不止一个返回值，就会通过栈来返回）
```

```
NSString *string1 = @"test 1";
NSString *string2 = @"test 2";
(lldb) po string1
test 1
(lldb) p string1
(NSString *) $2 = 0x0000000100003af0 @"test 1"
(lldb) p string2
(NSString *) $3 = 0x0000000100003b10 @"test 2"
```

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/69bba1b4-e1ec-4fbf-be83-654f1662786d/Untitled.png)

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/9f19aa76-4964-485b-93a0-b97ec35c2194/Untitled.png)
