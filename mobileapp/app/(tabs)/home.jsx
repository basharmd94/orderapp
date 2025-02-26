import { SafeAreaView } from "react-native-safe-area-context";
import { ScrollView, RefreshControl, Dimensions, Platform } from "react-native";
import { Box } from "@/components/ui/box";
import { Button } from "@/components/ui/button";
import { ButtonText, ButtonIcon } from "@/components/ui/button";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";
import { HStack } from "@/components/ui/hstack";
import { useAuth } from "@/context/AuthContext";
import { Heading } from "@/components/ui/heading";
import { LogOut, Package, Clock, RefreshCw, DollarSign, Plus, List, ChevronRight } from 'lucide-react-native';
import { Avatar } from "@/components/ui/avatar";
import { AvatarFallbackText } from "@/components/ui/avatar";
import { router } from "expo-router";
import { useState, useCallback, useEffect, useMemo } from 'react';
import { getOrderStats, getYearlyStats } from '@/lib/api_items';
import {
  LineChart,
  BarChart,
  PieChart,
} from "react-native-chart-kit";

// Import separated components
import LoadingState from '@/components/dashboard/LoadingState';
import StatsCard from '@/components/dashboard/StatsCard';
import ChartCard from '@/components/dashboard/ChartCard';
import QuickActionCard from '@/components/dashboard/QuickActionCard';

const screenWidth = Dimensions.get("window").width;

const Home = () => {
  const { user, logout, loading } = useAuth();
  const [refreshing, setRefreshing] = useState(false);
  const [yearlyStats, setYearlyStats] = useState(null);
  const [orderStats, setOrderStats] = useState({
    total: 150,
    pending: 25,
    completed: 125
  });
  const [statsLoading, setStatsLoading] = useState(true);

  // Transform monthly stats data for charts
  const chartData = useMemo(() => {
    if (!yearlyStats) {
      return {
        monthlyData: {
          labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
          datasets: [{
            data: [20, 45, 28, 80, 99, 43],
            color: (opacity = 1) => `rgba(255, 160, 1, ${opacity})`,
            strokeWidth: 2
          }],
        },
        orderTypeData: [
          {
            name: "Regular",
            orders: 45,
            color: "#FF6384",
            legendFontColor: "#7F7F7F",
            legendFontSize: 12
          },
          {
            name: "Express",
            orders: 25,
            color: "#36A2EB",
            legendFontColor: "#7F7F7F",
            legendFontSize: 12
          },
          {
            name: "Priority",
            orders: 30,
            color: "#FFCE56",
            legendFontColor: "#7F7F7F",
            legendFontSize: 12
          }
        ],
        dailyOrdersData: {
          labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
          datasets: [{
            data: [15, 12, 18, 25, 22, 20, 10]
          }]
        }
      };
    }

    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const monthlyData = new Array(12).fill(0);
    
    yearlyStats.monthly_stats.forEach(stat => {
      monthlyData[stat.month - 1] = stat.total_orders;
    });

    return {
      monthlyData: {
        labels: monthNames,
        datasets: [{
          data: monthlyData,
          color: (opacity = 1) => `rgba(255, 160, 1, ${opacity})`,
          strokeWidth: 2
        }],
      },
      orderTypeData: [
        {
          name: "Regular",
          orders: 45,
          color: "#FF6384",
          legendFontColor: "#7F7F7F",
          legendFontSize: 12
        },
        {
          name: "Express",
          orders: 25,
          color: "#36A2EB",
          legendFontColor: "#7F7F7F",
          legendFontSize: 12
        },
        {
          name: "Priority",
          orders: 30,
          color: "#FFCE56",
          legendFontColor: "#7F7F7F",
          legendFontSize: 12
        }
      ],
      dailyOrdersData: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        datasets: [{
          data: [15, 12, 18, 25, 22, 20, 10]
        }]
      }
    };
  }, [yearlyStats]);

  const fetchStats = async () => {
    try {
      setStatsLoading(true);
      const [stats, yearly] = await Promise.all([
        getOrderStats(),
        getYearlyStats()
      ]);
      setOrderStats(stats);
      setYearlyStats(yearly);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setStatsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const chartConfig = useMemo(() => ({
    backgroundGradientFrom: "#ffffff",
    backgroundGradientTo: "#ffffff",
    color: (opacity = 1) => `rgba(255, 160, 1, ${opacity})`,
    strokeWidth: 2,
    barPercentage: 0.8,
    useShadowColorFromDataset: false,
    decimalPlaces: 0,
    propsForLabels: {
      fontSize: 11,
      fontFamily: 'System',
      fontWeight: '500',
      color: '#64748b',
    },
    propsForBackgroundLines: {
      strokeDasharray: "6 6",
      stroke: "#f1f5f9",
      strokeWidth: 1,
    },
    fillShadowGradient: "#FFA001",
    fillShadowGradientOpacity: 0.3,
    labelColor: (opacity = 1) => `rgba(100, 116, 139, ${opacity})`,
  }), []);

  const stats = [
    { 
      title: "Total Orders", 
      value: statsLoading ? <RefreshCw className="animate-spin" size={20} color="white" /> : 
             yearlyStats ? yearlyStats.total_orders.toString() : "0", 
      color: "bg-gradient-to-br from-primary-500 via-primary-600 to-primary-700",
      icon: Package,
      trend: "+12.5%",
      trendUp: true
    },
    { 
      title: "Pending Orders", 
      value: statsLoading ? <RefreshCw className="animate-spin" size={20} color="white" /> : 
             yearlyStats ? yearlyStats.pending_orders.toString() : "0",
      color: "bg-gradient-to-br from-warning-500 via-warning-600 to-warning-700",
      icon: Clock,
      trend: "+5.2%",
      trendUp: true
    },
    { 
      title: "Total Revenue", 
      value: statsLoading ? <RefreshCw className="animate-spin" size={20} color="white" /> : 
             yearlyStats ? `৳${yearlyStats.total_amount.toLocaleString()}` : "৳0",
      color: "bg-gradient-to-br from-success-500 via-success-600 to-success-700",
      icon: DollarSign,
      trend: "+8.1%",
      trendUp: true
    },
  ];

  const quickActions = [
    { 
      title: "Create Order", 
      icon: Plus, 
      primary: true,
      onPress: () => router.push('/create-order'),
      description: "Create a new customer order",
    },
    { 
      title: "View Orders", 
      icon: List, 
      primary: false,
      onPress: () => router.push('/send-orders'),
      description: "Check order history",
    },
  ];

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchStats();
    setRefreshing(false);
  }, []);

  const getInitials = (name) => {
    if (!name) return 'U';
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase();
  };

  const getTimeOfDay = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  if (loading) {
    return (
      <SafeAreaView className="flex-1 bg-gray-50">
        <LoadingState />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <ScrollView 
        className="flex-1"
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        <Box className="px-4 py-4">
          {/* Enhanced Header Section */}
          <Box 
            className="bg-gray-800 rounded-3xl p-6 mb-6"
            style={{
              elevation: Platform.OS === 'android' ? 5 : 0,
            }}
          >
            <VStack space="md">
              <HStack className="justify-between items-start">
                <VStack space="xs">
                  <Text className="text-white text-base font-medium">
                    {getTimeOfDay()},
                  </Text>
                  <Heading size="xl" className="text-white">
                    {user?.employee_name || user?.user_name || 'User'}
                  </Heading>
                  <HStack space="sm" className="items-center mt-1">
                    <Box className="bg-white/30 px-3 py-1 rounded-full">
                      <Text className="text-white text-xs">
                        Terminal: {user?.terminal || 'N/A'}
                      </Text>
                    </Box>
                    <Box className="bg-white/30 px-3 py-1 rounded-full">
                      <Text className="text-white text-xs">
                        ID: {user?.user_id || 'N/A'}
                      </Text>
                    </Box>
                  </HStack>
                </VStack>
                <HStack space="sm">
                  <Avatar 
                    size="lg" 
                    className="border-2 border-white bg-white/30"
                  >
                    <AvatarFallbackText className="text-white">
                      {getInitials(user?.employee_name || 'User')}
                    </AvatarFallbackText>
                  </Avatar>
                  <Button
                    variant="solid"
                    size="sm"
                    onPress={logout}
                    className="bg-white/30 self-start mt-1"
                  >
                    <ButtonIcon as={LogOut} size={18} className="text-white" />
                  </Button>
                </HStack>
              </HStack>

              {/* User info card with gray-800 matching the Total Orders card */}
              <Box className="mt-4 bg-orange-500 p-4 rounded-2xl">
                <HStack className="justify-between items-center">
                  <Box className="items-start">
                    <Text className="text-white/80 text-xs">Business ID</Text>
                    <Text className="text-white font-bold">{user?.businessId || 'N/A'}</Text>
                  </Box>
                  
                  <Box className="w-[1px] h-8 bg-white/30" />
                  
                  <Box className="items-center">
                    <Text className="text-white/80 text-xs">Role</Text>
                    <Text className="text-white font-bold">{user?.is_admin || 'User'}</Text>
                  </Box>
                  
                  <Box className="w-[1px] h-8 bg-white/30" />
                  
                  <Box className="items-end">
                    <Text className="text-white/80 text-xs">Status</Text>
                    <Text className="text-white font-bold">{user?.status || 'N/A'}</Text>
                  </Box>
                </HStack>
              </Box>
            </VStack>
          </Box>

          {/* Stats Section with enhanced spacing and animations */}
          <VStack space="lg" className="mb-8">
            <HStack className="justify-between items-center mb-4">
              <VStack>
                <Heading size="sm" className="text-gray-800">Dashboard Overview</Heading>
                <Text className="text-gray-500 text-xs">Today's business summary</Text>
              </VStack>
              <Button
                variant="outline"
                size="sm"
                onPress={fetchStats}
                className="border-primary-100 bg-primary-50"
              >
                <HStack space="xs" className="items-center px-1">
                  <RefreshCw size={14} color = 'black' />
                  <ButtonText className="text-primary-500 text-sm">Refresh</ButtonText>
                </HStack>
              </Button>
            </HStack>
            <ScrollView 
              horizontal 
              showsHorizontalScrollIndicator={false}
              className="py-2"
              contentContainerStyle={{
                paddingRight: 16,
              }}
            >
              {stats.map((stat, index) => (
                <StatsCard key={index} stat={stat} index={index} />
              ))}
            </ScrollView>
          </VStack>

          {/* Charts Section */}
          <VStack space="lg" className="mb-8">
            <Heading size="sm" className="text-gray-800 mb-2">Analytics</Heading>
            
            {/* Monthly Orders Chart */}
            <ChartCard 
              title="Monthly Orders" 
              subtitle="+23.5% vs last month"
              subtitleColor="bg-primary-50"
            >
              <Box className="rounded-2xl overflow-hidden bg-gray-50/50 p-4">
                <LineChart
                  data={chartData.monthlyData}
                  width={screenWidth - 64}
                  height={220}
                  chartConfig={{
                    ...chartConfig,
                    propsForDots: {
                      r: "4",
                      stroke: "#FFA001",
                      strokeWidth: "2",
                      fill: "#fff"
                    }
                  }}
                  bezier
                  style={{
                    borderRadius: 16
                  }}
                  withHorizontalLines={true}
                  withVerticalLines={false}
                  withDots={true}
                  withShadow={true}
                  segments={5}
                  withInnerLines={true}
                  getDotColor={() => "#FFA001"}
                />
              </Box>
            </ChartCard>

            {/* Order Type Distribution */}
            <ChartCard 
              title="Order Distribution" 
              subtitle="Well balanced"
              subtitleColor="bg-success-50"
            >
              <Box className="rounded-2xl overflow-hidden bg-gray-50/50 p-4">
                <PieChart
                  data={chartData.orderTypeData}
                  width={screenWidth - 64}
                  height={220}
                  chartConfig={chartConfig}
                  accessor={"orders"}
                  backgroundColor={"transparent"}
                  paddingLeft={"15"}
                  center={[10, 0]}
                  absolute
                  hasLegend={true}
                  avoidFalseZero={true}
                />
              </Box>
            </ChartCard>

            {/* Daily Orders Chart */}
            <ChartCard 
              title="Daily Performance" 
              subtitle="Peak on Thursday"
              subtitleColor="bg-warning-50"
            >
              <Box className="rounded-2xl overflow-hidden bg-gray-50/50 p-4">
                <BarChart
                  data={chartData.dailyOrdersData}
                  width={screenWidth - 64}
                  height={220}
                  chartConfig={{
                    ...chartConfig,
                    barPercentage: 0.7,
                  }}
                  style={{
                    borderRadius: 16
                  }}
                  showBarTops={true}
                  showValuesOnTopOfBars={true}
                  fromZero={true}
                  withInnerLines={true}
                  segments={5}
                />
              </Box>
            </ChartCard>
          </VStack>

          {/* Quick Actions */}
          <VStack space="md">
            <HStack className="justify-between items-center mb-4">
              <VStack>
                <Heading size="sm" className="text-gray-800">Quick Actions</Heading>
                <Text className="text-gray-500 text-xs">Fast access to common tasks</Text>
              </VStack>
              <Button
                variant="link"
                size="sm"
                className="items-center"
              >
                <HStack space="xs" className="items-center">
                  <Text className="text-primary-500 text-sm">View All</Text>
                  <ChevronRight size={16} color = "gray" />
                </HStack>
              </Button>
            </HStack>
            <HStack>
              {quickActions.map((action, index) => (
                <QuickActionCard key={index} action={action} />
              ))}
            </HStack>
            
          </VStack>
        </Box>
      </ScrollView>
    </SafeAreaView>
  );
};

export default Home;


